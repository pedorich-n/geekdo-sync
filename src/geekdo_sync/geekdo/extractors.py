from typing import Dict, List

from .models import GeekdoItem, GeekdoItemId, GeekdoPlay, GeekdoPlayer


def extract_unique_items(plays: List[GeekdoPlay]) -> Dict[GeekdoItemId, GeekdoItem]:
    """
    Returns:
        Dictionary mapping item objectid to APIItem
    """
    items: Dict[GeekdoItemId, GeekdoItem] = {}
    for play in plays:
        item_id = play.item.objectid
        if item_id not in items:
            items[item_id] = play.item
    return items


def extract_unique_players(plays: List[GeekdoPlay]) -> Dict[str, GeekdoPlayer]:
    """
    Returns:
        Dictionary mapping player name to APIPlayer.
    """
    players: dict[str, GeekdoPlayer] = {}
    for play in plays:
        if not play.players:
            continue
        for player in play.players.player:
            if player.name not in players:
                players[player.name] = player
    return players


def extract_unique_locations(plays: List[GeekdoPlay]) -> List[str]:
    """
    Returns:
        Deduplicated list of non-None location strings across all plays.
    """
    seen: set[str] = set()
    locations: List[str] = []
    for play in plays:
        if play.location and play.location not in seen:
            seen.add(play.location)
            locations.append(play.location)
    return locations
