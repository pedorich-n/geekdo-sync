from datetime import date
from typing import Any, NewType, Optional

from pydantic import BaseModel, field_serializer

from geekdo_sync.utils import OptionalNonEmptyStr

from .utils import date_to_grist_date

GristId = NewType("GristId", int)
"""Type alias for Grist record IDs. To distinguish from other integers"""


class GristUpsertRecord(BaseModel):
    """Base model for Grist upsert records with require/fields structure."""

    require: dict[str, Any]
    fields: dict[str, Any]


class GristRecord(BaseModel):
    """Base model for Grist records with an ID."""

    id: GristId


class GristItemBase(BaseModel):
    ItemID: int  # GeekDo item id (unique key for upsert)
    Name: str  # Human-readable item name
    Subtype: str  # Choice (e.g., ['boardgame', 'boardgameimplementation'])
    Type: str  # Choice (e.g., 'thing', 'family')


class GristItemUpsert(GristItemBase):
    def to_upsert_record(self) -> GristUpsertRecord:
        return GristUpsertRecord(
            require={"ItemID": self.ItemID},
            fields={
                "Name": self.Name,
                "Subtype": self.Subtype,
                "Type": self.Type,
            },
        )


class GristItemOutput(GristRecord, GristItemBase):
    pass


class GristPlayerBase(BaseModel):
    Name: str  # Human-readable name (unique key for upsert)
    Username: OptionalNonEmptyStr = None  # GeekDo username
    UserID: Optional[int] = None  # GeekDo userid


class GristPlayerUpsert(GristPlayerBase):
    def to_upsert_record(self) -> GristUpsertRecord:
        return GristUpsertRecord(
            require={"Name": self.Name},
            fields={
                "Username": self.Username,
                "UserID": self.UserID,
            },
        )


class GristPlayerOutput(GristRecord, GristPlayerBase):
    pass


class GristPlayerPlayBase(BaseModel):
    Play: GristId  # Reference to Play record
    Player: GristId  # Reference to Player record
    StartPosition: OptionalNonEmptyStr = None
    Color: OptionalNonEmptyStr = None
    Score: Optional[int] = None
    Rating: Optional[int] = None
    New: Optional[bool] = None
    Win: Optional[bool] = None


class GristPlayerPlayUpsert(GristPlayerPlayBase):
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


class GristPlayerPlayOutput(GristRecord, GristPlayerPlayBase):
    pass


class GristPlayBase(BaseModel):
    PlayID: int  # GeekDo play id (unique key for upsert)
    Date: date
    Item: GristId  # Reference to Item record
    Quantity: Optional[int] = None
    Length_Minutes: Optional[int] = None
    Comment: OptionalNonEmptyStr = None
    Location: OptionalNonEmptyStr = None


class GristPlayUpsert(GristPlayBase):
    @field_serializer("Date")
    def serialize_Date(self, value: date) -> int:
        return date_to_grist_date(value)

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


class GristPlayOutput(GristRecord, GristPlayBase):
    pass
