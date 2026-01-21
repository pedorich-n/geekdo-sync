import logging
import time
from datetime import date, timedelta
from typing import Dict, List, Optional, Set

from src.geekdo.client import BGGClient
from src.geekdo.extractors import extract_unique_items, extract_unique_players
from src.geekdo.models import APIItem, APIPlay, ItemId, PlayId
from src.grist.client import GristClient
from src.grist.models import (
    GristId,
    GristItemUpsert,
    GristPlayerPlayUpsert,
    GristPlayerUpsert,
    GristPlayUpsert,
)

logger = logging.getLogger(__name__)


class GristSync:
    """Orchestrates incremental synchronization of GeekDo play data to Grist."""

    def __init__(self, bgg_client: BGGClient, bgg_username: str, grist_client: GristClient):
        self.bgg_client = bgg_client
        self.bgg_username = bgg_username
        self.grist_client = grist_client
        self.overlap_detection_limit = 100

    def get_recent_plays_from_grist(self) -> Dict[PlayId, GristId]:
        try:
            plays = self.grist_client.get_plays(
                sort_by="-Date",
                limit=self.overlap_detection_limit,
            )

            play_id_mapping: Dict[PlayId, GristId] = {PlayId(play.PlayID): play.id for play in plays}

            logger.info(f"Retrieved {len(play_id_mapping)} recent plays for overlap detection")
            return play_id_mapping

        except Exception as e:
            logger.error(f"Failed to fetch recent plays from Grist: {e}")
            return {}

    def get_most_recent_play_date(self) -> Optional[date]:
        try:
            plays = self.grist_client.get_plays(
                sort_by="-Date",
                limit=1,
            )

            if not plays:
                return None

            result = plays[0].Date

            logger.debug(f"Most recent play date: {result}")
            return result

        except Exception as e:
            logger.error(f"Failed to fetch most recent play date from Grist: {e}")
            return None

    def fetch_new_plays_until_overlap(
        self,
        existing_play_ids: Set[PlayId],
        mindate: Optional[date] = None,
    ) -> List[APIPlay]:
        """
        Fetch new plays from API using iterate-until-overlap strategy.

        Paginates through API pages until overlap with existing plays is detected,
        then stops and returns only the new plays.

        Args:
            existing_play_ids: Set of existing play IDs from Grist
            mindate: Optional minimum date to start fetching from (for optimization)

        Returns:
            List of new APIPlay objects that don't exist in Grist
        """
        new_plays: List[APIPlay] = []
        page = 1
        found_overlap = False

        logger.info(f"Starting iterate-until-overlap fetch (mindate: {mindate})")

        while not found_overlap:
            if page > 1:
                time.sleep(self.bgg_client.delay)

            logger.debug(f"Fetching page {page}")
            response = self.bgg_client.get_plays(
                username=self.bgg_username,
                page=page,
                mindate=mindate,
            )

            if not response.play:
                logger.debug("No plays in response, reached end of data")
                break

            # Intersect current page play IDs with existing play IDs. If the resulting set is non-empty, there's an overlap.
            page_play_ids = {play.id for play in response.play}
            overlap = page_play_ids & existing_play_ids

            if overlap:
                logger.info(f"Found overlap on page {page} ({len(overlap)} plays already exist)")
                # Filter to only NEW plays from this page
                page_new_plays = [play for play in response.play if play.id not in existing_play_ids]
                new_plays.extend(page_new_plays)
                found_overlap = True
                logger.info(f"Stopping pagination. Found {len(page_new_plays)} new plays on final page")
            else:
                # All plays on this page are new
                new_plays.extend(response.play)
                logger.debug(f"Page {page}: all {len(response.play)} plays are new")

            if len(response.play) < 100:
                logger.debug(f"Page {page} has < 100 plays, reached end of user's play history")
                break

            if found_overlap:
                break

            page += 1

        logger.info(f"Collected {len(new_plays)} new plays total")
        return new_plays

    def prepare_items(self, plays: List[APIPlay]) -> Dict[ItemId, GristItemUpsert]:
        api_items: Dict[ItemId, APIItem] = extract_unique_items(plays)

        items_dict = {
            objectid: GristItemUpsert(
                ItemID=item.objectid,
                Name=item.name,
                Subtype=item.subtype,
                Type=item.objecttype,
            )
            for objectid, item in api_items.items()
        }

        logger.debug(f"Prepared {len(items_dict)} unique items")
        return items_dict

    def prepare_players(self, plays: List[APIPlay]) -> Dict[str, GristPlayerUpsert]:
        """
        Returns:
            Dictionary mapping player name to GristPlayerUpsert.
        """
        api_players = extract_unique_players(plays)

        players_dict = {
            name: GristPlayerUpsert(Name=player.name, Username=player.username, UserID=player.userid)
            for name, player in api_players.items()
        }

        logger.debug(f"Prepared {len(players_dict)} unique players")
        return players_dict

    def prepare_plays(self, plays: List[APIPlay], items_mapping: Dict[ItemId, GristId]) -> List[GristPlayUpsert]:
        plays_list: List[GristPlayUpsert] = []

        for play in plays:
            item_id = play.item.objectid
            if item_id not in items_mapping:
                logger.warning(f"Item {item_id} not found in items_mapping for play {play.id}")
                continue

            play_input = GristPlayUpsert(
                PlayID=play.id,
                Date=play.date,
                Item=items_mapping[item_id],
                Quantity=play.quantity,
                Length_Minutes=play.length,
                Comment=play.comments,
                Location=play.location,
            )
            plays_list.append(play_input)

        logger.debug(f"Prepared {len(plays_list)} plays")
        return plays_list

    def prepare_player_plays(
        self,
        plays: List[APIPlay],
        plays_mapping: Dict[PlayId, GristId],
        players_mapping: Dict[str, GristId],
    ) -> List[GristPlayerPlayUpsert]:
        player_plays_list: List[GristPlayerPlayUpsert] = []

        for play in plays:
            play_id = play.id
            if play_id not in plays_mapping:
                logger.warning(f"Play {play_id} not found in plays_mapping")
                continue

            if not play.players:
                continue

            for player in play.players.player:
                if player.name not in players_mapping:
                    logger.warning(f"Player '{player.name}' not found in players_mapping for play {play_id}")
                    continue

                player_play = GristPlayerPlayUpsert(
                    Play=plays_mapping[play_id],
                    Player=players_mapping[player.name],
                    StartPosition=player.startposition,
                    Color=player.color,
                    Score=player.score,
                    Rating=player.rating,
                    New=player.new,
                    Win=player.win,
                )
                player_plays_list.append(player_play)

        logger.debug(f"Prepared {len(player_plays_list)} player-play relationships")
        return player_plays_list

    def sync_players(self, new_players: Dict[str, GristPlayerUpsert]) -> Dict[str, GristId]:
        """
        Args:
            new_players: Players to upsert (by name)

        Returns:
            Complete players mapping (name → grist_row_id) after upsert
        """
        if not new_players:
            logger.debug("No players to sync")
            return {}

        logger.debug(f"Upserting {len(new_players)} players to Grist")

        self.grist_client.upsert_players(list(new_players.values()))

        players = self.grist_client.get_players(limit=None)

        players_mapping: Dict[str, GristId] = {player.Name: player.id for player in players}

        logger.debug(f"Players mapping contains {len(players_mapping)} entries")
        return players_mapping

    def sync_items(self, new_items: Dict[ItemId, GristItemUpsert]) -> Dict[ItemId, GristId]:
        """
        Args:
            new_items: Items to upsert (by objectid)

        Returns:
            Complete items mapping (geekdo_item_id → grist_row_id) after upsert
        """
        if not new_items:
            logger.debug("No items to sync")
            return {}

        logger.debug(f"Upserting {len(new_items)} items to Grist")

        self.grist_client.upsert_items(list(new_items.values()))

        items = self.grist_client.get_items(limit=None)

        items_mapping: Dict[ItemId, GristId] = {ItemId(item.ItemID): item.id for item in items}

        logger.debug(f"Items mapping contains {len(items_mapping)} entries")
        return items_mapping

    def sync_plays(
        self,
        plays_list: List[GristPlayUpsert],
        existing_play_ids: Dict[PlayId, GristId],
    ) -> Dict[PlayId, GristId]:
        """
        Args:
            plays_list: List of plays with resolved item references
            existing_play_ids: Existing plays mapping (geekdo_play_id → grist_row_id)

        Returns:
            Complete plays mapping (geekdo_play_id → grist_row_id) after insert
        """
        # Filter out plays that already exist
        plays_to_insert = [play for play in plays_list if play.PlayID not in existing_play_ids]

        if not plays_to_insert:
            logger.debug("No new plays to sync")
            return existing_play_ids

        logger.debug(f"Inserting {len(plays_to_insert)} new plays to Grist")

        self.grist_client.upsert_plays(plays_to_insert)

        plays = self.grist_client.get_plays(limit=None)

        plays_mapping: Dict[PlayId, GristId] = {PlayId(play.PlayID): play.id for play in plays}

        logger.debug(f"Plays mapping contains {len(plays_mapping)} entries")
        return plays_mapping

    def sync_player_plays(
        self,
        player_plays_list: List[GristPlayerPlayUpsert],
    ) -> None:
        if not player_plays_list:
            logger.debug("No player-plays to sync")
            return

        logger.debug(f"Upserting {len(player_plays_list)} player-play relationships to Grist")

        self.grist_client.upsert_player_plays(player_plays_list)
        logger.debug(f"Upserted {len(player_plays_list)} player-play relationships")

    def validate_sync(self) -> bool:
        """
        Validate that all inserts completed successfully.

        Performs the following checks:
        - All tables have records
        - All plays reference valid items
        - All player-plays reference valid plays and players
        - No orphaned records

        Returns:
            True if validation passed, False otherwise
        """
        try:
            logger.info("Running sync validation checks")
            validation_passed = True

            # Check 1: Verify all tables have data
            logger.debug("Check 1: Verifying table record counts")
            items = self.grist_client.get_items(limit=None)
            players = self.grist_client.get_players(limit=None)
            plays = self.grist_client.get_plays(limit=None)
            player_plays = self.grist_client.get_player_plays(limit=None)

            items_count = len(items)
            players_count = len(players)
            plays_count = len(plays)
            player_plays_count = len(player_plays)

            logger.info(f"  Items: {items_count}")
            logger.info(f"  Players: {players_count}")
            logger.info(f"  Plays: {plays_count}")
            logger.info(f"  PlayerPlays: {player_plays_count}")

            if plays_count == 0:
                logger.warning("  Warning: No plays in Plays table")

            # Check 2: Verify referential integrity for Plays → Items
            logger.debug("Check 2: Validating Plays → Items references")
            valid_item_ids = {item.id for item in items}
            invalid_play_items = []

            for play in plays:
                if play.Item not in valid_item_ids:
                    invalid_play_items.append((play.id, play.PlayID, play.Item))

            if invalid_play_items:
                logger.error(f"  Found {len(invalid_play_items)} plays with invalid item references:")
                for grist_id, play_id, item_ref in invalid_play_items[:5]:
                    logger.error(f"    Play {play_id} (id={grist_id}) references non-existent item {item_ref}")
                validation_passed = False
            else:
                logger.debug("  All plays have valid item references")

            # Check 3: Verify referential integrity for PlayerPlays → Plays and Players
            logger.debug("Check 3: Validating PlayerPlays → Plays and Players references")
            valid_play_ids = {play.id for play in plays}
            valid_player_ids = {player.id for player in players}
            invalid_player_plays = []

            for pp in player_plays:
                if pp.Play not in valid_play_ids:
                    invalid_player_plays.append(("play", pp.id, pp.Play))
                if pp.Player not in valid_player_ids:
                    invalid_player_plays.append(("player", pp.id, pp.Player))

            if invalid_player_plays:
                logger.error(f"  Found {len(invalid_player_plays)} player-plays with invalid references:")
                for ref_type, grist_id, ref_id in invalid_player_plays[:5]:
                    logger.error(f"    PlayerPlay id={grist_id} references non-existent {ref_type} {ref_id}")
                validation_passed = False
            else:
                logger.debug("  All player-plays have valid references")

            # Check 4: Verify no duplicate PlayIDs
            logger.debug("Check 4: Checking for duplicate PlayIDs")
            play_ids_seen: Set[int] = set()
            duplicate_play_ids: List[int] = []

            for play in plays:
                if play.PlayID in play_ids_seen:
                    duplicate_play_ids.append(play.PlayID)
                play_ids_seen.add(play.PlayID)

            if duplicate_play_ids:
                logger.error(f"  Found {len(duplicate_play_ids)} duplicate PlayIDs:")
                for play_id in duplicate_play_ids[:5]:
                    logger.error(f"    Duplicate PlayID: {play_id}")
                validation_passed = False
            else:
                logger.debug("  No duplicate PlayIDs found")

            # Check 5: Verify no duplicate ItemIDs
            logger.debug("Check 5: Checking for duplicate ItemIDs")
            item_ids_seen: Set[int] = set()
            duplicate_item_ids: List[int] = []

            for item in items:
                if item.ItemID in item_ids_seen:
                    duplicate_item_ids.append(item.ItemID)
                item_ids_seen.add(item.ItemID)

            if duplicate_item_ids:
                logger.error(f"  Found {len(duplicate_item_ids)} duplicate ItemIDs:")
                for item_id in duplicate_item_ids[:5]:
                    logger.error(f"    Duplicate ItemID: {item_id}")
                validation_passed = False
            else:
                logger.debug("  No duplicate ItemIDs found")

            if validation_passed:
                logger.info("✓ All validation checks passed")
            else:
                logger.error("✗ Validation failed - data integrity issues detected")

            return validation_passed

        except Exception as e:
            logger.error(f"Validation failed with exception: {e}", exc_info=True)
            return False

    def run_sync(self) -> bool:
        """
        Returns:
            True if sync completed successfully, False otherwise
        """
        logger.info(f"Starting Grist sync for user '{self.bgg_username}'")

        try:
            # Phase 1: Get recent plays and determine mindate
            logger.info("Phase 1: Fetching recent plays from Grist")
            recent_play_ids_dict = self.get_recent_plays_from_grist()
            recent_play_ids_set = set(recent_play_ids_dict.keys())

            # Only use mindate optimization for incremental sync with existing plays
            # For initial/full sync, fetch ALL history (mindate=None)
            if not recent_play_ids_set:
                logger.info("No existing plays in Grist, performing FULL sync (all history)")
                mindate = None
            else:
                logger.info(f"Found {len(recent_play_ids_set)} recent plays in Grist")
                most_recent_date = self.get_most_recent_play_date()
                if most_recent_date:
                    # Use 1 day buffer to handle timezone differences and deleted/edited plays
                    mindate = most_recent_date - timedelta(days=1)
                    logger.info(f"Using mindate optimization for incremental sync: {mindate}")
                else:
                    # Shouldn't happen (we have play IDs but no dates), but be safe
                    logger.warning("Have play IDs but no date found - performing full sync")
                    mindate = None

            # Phase 2: Fetch only new plays using iterate-until-overlap
            logger.info("Phase 2: Fetching new plays from BGG API")
            new_plays = self.fetch_new_plays_until_overlap(
                existing_play_ids=recent_play_ids_set,
                mindate=mindate,
            )

            if not new_plays:
                logger.info("No new plays found, sync complete")
                return True

            logger.info(f"Found {len(new_plays)} new plays to sync")

            # Phase 3: Prepare independent entities
            logger.info("Phase 3: Preparing independent entities")
            items_dict = self.prepare_items(new_plays)
            players_dict = self.prepare_players(new_plays)

            # Phase 4: Sync independent entities and get their IDs
            logger.info("Phase 4: Syncing independent entities to Grist")
            logger.debug("Syncing players...")
            players_mapping = self.sync_players(players_dict)

            logger.debug("Syncing items...")
            items_mapping = self.sync_items(items_dict)

            # Phase 5: Prepare and sync dependent entities
            logger.info("Phase 5: Preparing and syncing dependent entities")
            plays_list = self.prepare_plays(new_plays, items_mapping)
            plays_mapping = self.sync_plays(plays_list, recent_play_ids_dict)

            player_plays_list = self.prepare_player_plays(new_plays, plays_mapping, players_mapping)
            self.sync_player_plays(player_plays_list)

            # Phase 6: Validation
            logger.info("Phase 6: Validating sync")
            if self.validate_sync():
                logger.info("Sync completed successfully")
                return True
            else:
                logger.error("Validation failed")
                return False

        except Exception as e:
            logger.error(f"Sync failed with error: {e}", exc_info=True)
            return False
