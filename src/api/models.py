from datetime import date as Date
from typing import Optional

from pydantic import ConfigDict, field_validator
from pydantic_xml import BaseXmlModel, attr, element


class APISubtype(BaseXmlModel, tag="subtype"):
    value: str = attr()


class APISubtypes(BaseXmlModel, tag="subtypes"):
    subtype: list[APISubtype] = element(default_factory=list)


class APIItem(BaseXmlModel, tag="item"):
    model_config = ConfigDict(populate_by_name=True)

    name: str = attr()
    objecttype: str = attr() 
    objectid: int = attr()
    subtypes: APISubtypes = element()


class APIPlayer(BaseXmlModel, tag="player"):
    username: Optional[str] = attr(default=None)
    userid: Optional[int] = attr(default=None)
    name: Optional[str] = attr(default=None)
    startposition: Optional[str] = attr(default=None)
    color: Optional[str] = attr(default=None)
    score: Optional[int] = attr(default=None)
    new: Optional[bool] = attr(default=None)
    rating: Optional[int] = attr(default=None)
    win: Optional[bool] = attr(default=None)

    @field_validator("username", "userid", "name", "startposition", "color", "score", "rating", mode="before")
    @classmethod
    def convert_empty_numeric_strings(cls, v: str | int) -> Optional[str | int]:
        return None if v == "" else v


class APIPlayers(BaseXmlModel, tag="players"):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    player: list[APIPlayer] = element(default_factory=list)


class APIPlay(BaseXmlModel, tag="play"):
    """Play element in API response."""

    id: int = attr()
    date: Date = attr()
    quantity: int = attr()
    length: int = attr()
    incomplete: bool = attr()
    nowinstats: bool = attr()
    location: Optional[str] = attr(default=None)
    item: APIItem = element()
    comments: Optional[str] = element(default=None)
    players: Optional[APIPlayers] = element(default=None)

    @field_validator("location", "comments", mode="before")
    @classmethod
    def convert_empty_strings(cls, v: str) -> Optional[str]:
        return None if v == "" else v


class APIPlaysResponse(BaseXmlModel, tag="plays"):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    username: str = attr()
    userid: int = attr()
    total: int = attr()
    page: int = attr()
    play: list[APIPlay] = element(default_factory=list)
