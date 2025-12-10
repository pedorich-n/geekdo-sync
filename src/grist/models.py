from datetime import date as Date
from typing import Optional

from pydantic import BaseModel, Field

# Input models (for syncing to Grist - no Grist row IDs)


class GristItemInput(BaseModel):
    """Input model for Item record - used when syncing data to Grist."""

    item_id: str  # GeekDo item id
    name: str  # Human-readable item name
    subtype: list[str] = Field(default_factory=list)  # Choice list (e.g., ['boardgame', 'boardgameimplementation'])
    type: str  # Choice (e.g., 'thing', 'family')


class GristPlayerInput(BaseModel):
    """Input model for Player record - used when syncing data to Grist."""

    username: Optional[str] = None  # GeekDo username
    user_id: Optional[str] = None  # GeekDo userid
    name: str  # Human-readable name


class GristPlayerPlayInput(BaseModel):
    """Input model for PlayerPlay record - used when syncing data to Grist."""

    play_id: int  # Reference to Play record
    player_id: int  # Reference to Player record
    start_position: Optional[str] = None
    color: Optional[str] = None
    score: Optional[int] = None
    rating: Optional[int] = None
    new: Optional[bool] = None
    win: Optional[bool] = None


class GristPlayInput(BaseModel):
    """Input model for Play record - used when syncing data to Grist."""

    play_id: str  # GeekDo play id
    date: Date
    item_id: int  # Reference to Item record
    quantity: int
    length_minutes: Optional[int] = None
    comment: Optional[str] = None
    location: Optional[str] = None


# Output models (for reading from Grist - includes Grist row IDs)


class GristItemOutput(GristItemInput):
    """Output model for Item record - includes Grist row ID."""

    id: int  # Grist row ID


class GristPlayerOutput(GristPlayerInput):
    """Output model for Player record - includes Grist row ID."""

    id: int  # Grist row ID


class GristPlayerPlayOutput(GristPlayerPlayInput):
    """Output model for PlayerPlay record - includes Grist row ID."""

    id: int  # Grist row ID


class GristPlayOutput(GristPlayInput):
    """Output model for Play record - includes Grist row ID."""

    id: int  # Grist row ID
