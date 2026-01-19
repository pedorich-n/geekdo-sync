from datetime import date as Date
from typing import Annotated, Any, List, NewType, Optional

from pydantic import BeforeValidator, ConfigDict, computed_field
from pydantic_xml import BaseXmlModel, attr, element

from src.utils import NonEmptyStr, OptionalFromNonEmptyStr, OptionalNonEmptyStr

UserId = NewType("UserId", int)
"""Type alias for BoardGameGeek user IDs. To distinguish from other integers"""

PlayId = NewType("PlayId", int)
"""Type alias for BoardGameGeek play IDs. To distinguish from other integers"""


def _parse_optional_id(val: Any) -> Optional[int]:
    if isinstance(val, str):
        val = val.strip()
        if val == "" or val == "0":
            return None
        else:
            return int(val)
    elif isinstance(val, int):
        if val == 0:
            return None
        else:
            return int(val)

    return None


def _parse_optional_user_id(val: Any) -> Optional[UserId]:
    res = _parse_optional_id(val)
    if res is None:
        return None
    return UserId(res)


def _parse_user_id(val: Any) -> UserId:
    res = _parse_optional_id(val)
    if res is None:
        raise ValueError("UserId cannot be empty or zero")
    return UserId(res)


def _parse_play_id(val: Any) -> PlayId:
    res = _parse_optional_id(val)
    if res is None:
        raise ValueError("PlayId cannot be empty or zero")
    return PlayId(res)


class APISubtype(BaseXmlModel, tag="subtype"):
    value: str = attr()


class APISubtypes(BaseXmlModel, tag="subtypes"):
    subtype: List[APISubtype] = element(default_factory=list)


class APIItem(BaseXmlModel, tag="item"):
    model_config = ConfigDict(populate_by_name=True)

    name: str = attr()
    objecttype: str = attr()
    objectid: str = attr()
    subtypes: APISubtypes = element()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def subtype(self) -> str:
        return self.subtypes.subtype[0].value if self.subtypes.subtype else ""


class APIPlayer(BaseXmlModel, tag="player"):
    username: OptionalNonEmptyStr = attr(default=None)
    userid: Annotated[Optional[UserId], BeforeValidator(_parse_optional_id)] = attr(default=None)
    name: OptionalNonEmptyStr = attr()
    startposition: OptionalNonEmptyStr = attr(default=None)
    color: OptionalNonEmptyStr = attr(default=None)
    score: OptionalFromNonEmptyStr[int] = attr(default=None)
    new: OptionalFromNonEmptyStr[bool] = attr(default=None)
    rating: OptionalFromNonEmptyStr[int] = attr(default=None)
    win: OptionalFromNonEmptyStr[bool] = attr(default=None)


class APIPlayers(BaseXmlModel, tag="players"):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    player: List[APIPlayer] = element(default_factory=list)


class APIPlay(BaseXmlModel, tag="play"):
    """Play element in API response."""

    id: Annotated[PlayId, BeforeValidator(_parse_play_id)] = attr()
    date: Date = attr()
    quantity: OptionalFromNonEmptyStr[int] = attr()
    length: OptionalFromNonEmptyStr[int] = attr()
    incomplete: OptionalFromNonEmptyStr[bool] = attr()
    nowinstats: OptionalFromNonEmptyStr[bool] = attr()
    location: OptionalNonEmptyStr = attr(default=None)
    item: APIItem = element()
    comments: OptionalNonEmptyStr = element(default=None)
    players: Optional[APIPlayers] = element(default=None)


class APIPlaysResponse(BaseXmlModel, tag="plays"):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    username: NonEmptyStr = attr()
    userid: Annotated[UserId, BeforeValidator(_parse_user_id)] = attr()
    total: int = attr()
    page: int = attr()
    play: List[APIPlay] = element(default_factory=list)
