from datetime import UTC, date, datetime, time


def date_to_grist_date(d: date) -> int:
    """
    Grist stores dates as UTC timestamps at midnight.
    """
    return int(datetime.combine(d, time.min, tzinfo=UTC).timestamp())
