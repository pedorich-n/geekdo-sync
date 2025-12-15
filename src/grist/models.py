from datetime import date
from typing import Any, Optional

from pydantic import BaseModel

# Grist Input models (for writing to Grist)

class GristUpsertRecord(BaseModel):
    """Base model for Grist upsert records with require/fields structure."""

    require: dict[str, Any]
    fields: dict[str, Any]


class GristItemInput(BaseModel):
    """Input model for Item record - used when syncing data to Grist."""

    ItemID: str  # GeekDo item id (unique key for upsert)
    Name: str  # Human-readable item name
    Subtype: str  # Choice (e.g., ['boardgame', 'boardgameimplementation'])
    Type: str  # Choice (e.g., 'thing', 'family')

    def to_upsert_record(self) -> GristUpsertRecord:
        return GristUpsertRecord(
            require={"ItemID": self.ItemID},
            fields={
                "Name": self.Name,
                "Subtype": self.Subtype,
                "Type": self.Type,
            },
        )


class GristPlayerInput(BaseModel):
    """Input model for Player record - used when syncing data to Grist."""

    Name: str  # Human-readable name (unique key for upsert)
    Username: Optional[str] = None  # GeekDo username
    UserID: Optional[str] = None  # GeekDo userid

    def to_upsert_record(self) -> GristUpsertRecord:
        return GristUpsertRecord(
            require={"Name": self.Name},
            fields={
                "Username": self.Username,
                "UserID": self.UserID,
            },
        )


class GristPlayerPlayInput(BaseModel):
    """Input model for PlayerPlay record - used when syncing data to Grist."""

    Play: int  # Reference to Play record
    Player: int  # Reference to Player record
    StartPosition: Optional[str] = None
    Color: Optional[str] = None
    Score: Optional[int] = None
    Rating: Optional[int] = None
    New: Optional[bool] = None
    Win: Optional[bool] = None

    def to_upsert_record(self) -> GristUpsertRecord:
        return GristUpsertRecord(
            require={
                "Play": self.Play,
                "Player": self.Player,
            },
            fields={
                "StartPosition": self.StartPosition,
                "Color": self.Color,
                "Score": self.Score,
                "Rating": self.Rating,
                "New": self.New,
                "Win": self.Win,
            },
        )


class GristPlayInput(BaseModel):
    """Input model for Play record - used when syncing data to Grist."""

    PlayID: str  # GeekDo play id (unique key for upsert)
    Date: date
    Item: int  # Reference to Item record
    Quantity: int
    Length_Minutes: Optional[int] = None
    Comment: Optional[str] = None
    Location: Optional[str] = None

    def to_upsert_record(self) -> GristUpsertRecord:
        return GristUpsertRecord(
            require={"PlayID": self.PlayID},
            fields={
                "Date": self.Date,
                "Item": self.Item,
                "Quantity": self.Quantity,
                "Length_Minutes": self.Length_Minutes,
                "Comment": self.Comment,
                "Location": self.Location,
            },
        )

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
