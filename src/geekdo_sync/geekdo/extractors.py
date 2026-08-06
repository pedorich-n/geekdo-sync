from .models import GeekdoItem, GeekdoItemId, GeekdoPlay, GeekdoPlayer


def extract_unique_items(plays: list[GeekdoPlay]) -> dict[GeekdoItemId, GeekdoItem]:
    """
    Returns:
        Dictionary mapping item objectid to APIItem
    """
    items: dict[GeekdoItemId, GeekdoItem] = {}
    for play in plays:
        item_id = play.item.objectid
        if item_id not in items:
            items[item_id] = play.item
    return items


def extract_unique_players(plays: list[GeekdoPlay]) -> dict[str, GeekdoPlayer]:
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


def extract_unique_locations(plays: list[GeekdoPlay]) -> set[str]:
    """
    Returns:
        Deduplicated set of non-None location strings across all plays.
    """
    return {play.location for play in plays if play.location}
