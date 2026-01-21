import logging
from typing import List, Optional, Type

from pydantic import PositiveInt
from pygrister.api import GristApi  # type: ignore[import-untyped]

from src.config import GristConfig
from src.grist.models import (
    GristItemOutput,
    GristItemUpsert,
    GristPlayerOutput,
    GristPlayerPlayOutput,
    GristPlayerPlayUpsert,
    GristPlayerUpsert,
    GristPlayOutput,
    GristPlayUpsert,
    GristRecord,
    GristUpsertRecord,
)
from src.utils import OptionalNonEmptyStr


class GristClient:
    def __init__(self, config: GristConfig):
        self.logger = logging.getLogger(__name__)
        self.api = GristApi(config=config.get_pygrister_config())

        self.items_table_id = "Items"
        self.players_table_id = "Players"
        self.plays_table_id = "Plays"
        self.player_plays_table_id = "PlayerPlays"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.api.close_session()
        return False

    def _fetch_records[R: GristRecord](
        self,
        table_id: str,
        model_class: Type[R],
        entity_name: str,
        sort_by: OptionalNonEmptyStr,
        limit: Optional[PositiveInt],
    ) -> List[R]:
        try:
            _, records_result = self.api.list_records(
                table_id=table_id,
                limit=limit or 0,
                sort=sort_by,
            )
            decoded = [model_class.model_validate(record) for record in records_result]

            self.logger.debug(f"Fetched {len(decoded)} {entity_name} from Grist")

            return decoded

        except Exception as e:
            self.logger.error(f"Failed to fetch {entity_name} from Grist: {e}", exc_info=True)
            return []

    def _upsert_records[R: GristUpsertRecord](
        self,
        table_id: str,
        records: List[R],
        entity_name: str,
    ) -> None:
        try:
            upsert_records = [record.model_dump() for record in records]
            self.api.add_update_records(table_id=table_id, records=upsert_records)

            self.logger.debug(f"Upserted {len(records)} {entity_name} to Grist")

        except Exception as e:
            self.logger.error(f"Failed to upsert {entity_name} to Grist: {e}", exc_info=True)

    def get_plays(self, sort_by: OptionalNonEmptyStr = "-Date", limit: Optional[PositiveInt] = 100) -> List[GristPlayOutput]:
        return self._fetch_records(self.plays_table_id, GristPlayOutput, "plays", sort_by, limit)

    def get_players(self, sort_by: OptionalNonEmptyStr = None, limit: Optional[PositiveInt] = 100) -> List[GristPlayerOutput]:
        return self._fetch_records(self.players_table_id, GristPlayerOutput, "players", sort_by, limit)

    def get_items(self, sort_by: OptionalNonEmptyStr = None, limit: Optional[PositiveInt] = 100) -> List[GristItemOutput]:
        return self._fetch_records(self.items_table_id, GristItemOutput, "items", sort_by, limit)

    def get_player_plays(self, sort_by: OptionalNonEmptyStr = None, limit: Optional[PositiveInt] = 100) -> List[GristPlayerPlayOutput]:
        return self._fetch_records(self.player_plays_table_id, GristPlayerPlayOutput, "player plays", sort_by, limit)

    def upsert_items(self, items: List[GristItemUpsert]) -> None:
        upsert_records = [item.to_upsert_record() for item in items]
        self._upsert_records(self.items_table_id, upsert_records, "items")

    def upsert_players(self, players: List[GristPlayerUpsert]) -> None:
        upsert_records = [player.to_upsert_record() for player in players]
        self._upsert_records(self.players_table_id, upsert_records, "players")

    def upsert_plays(self, plays: List[GristPlayUpsert]) -> None:
        upsert_records = [play.to_upsert_record() for play in plays]
        self._upsert_records(self.plays_table_id, upsert_records, "plays")

    def upsert_player_plays(self, player_plays: List[GristPlayerPlayUpsert]) -> None:
        upsert_records = [player_play.to_upsert_record() for player_play in player_plays]
        self._upsert_records(self.player_plays_table_id, upsert_records, "player plays")
