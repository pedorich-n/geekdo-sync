from typing import Dict, List

from .models import APIItem, APIPlay, APIPlayer, ItemId


def extract_unique_items(plays: List[APIPlay]) -> Dict[ItemId, APIItem]:
    """
    Extract all unique items from plays.

    Args:
        plays: List of API play objects

    Returns:
        Dictionary mapping item objectid to APIItem
    """
    items: Dict[ItemId, APIItem] = {}
    for play in plays:
        item_id = play.item.objectid
        if item_id not in items:
            items[item_id] = play.item
    return items


def extract_unique_players(plays: List[APIPlay]) -> Dict[str, APIPlayer]:
    """
    Extract all unique players from plays.

    Args:
        plays: List of API play objects

    Returns:
        Dictionary mapping player name to APIPlayer.
    """
    players: dict[str, APIPlayer] = {}
    for play in plays:
        if not play.players:
            continue
        for player in play.players.player:
            if player.name not in players:
                players[player.name] = player
    return players
