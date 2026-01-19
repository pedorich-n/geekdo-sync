from datetime import date, datetime, time, timezone


def date_to_grist_date(d: date) -> int:
    """
    Grist stores dates as UTC timestamps at midnight.
    """
    return int(datetime.combine(d, time.min, tzinfo=timezone.utc).timestamp())
