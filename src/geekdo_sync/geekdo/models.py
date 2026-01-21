from datetime import date as Date
from typing import Annotated, Any, List, NewType, Optional

from pydantic import BeforeValidator, ConfigDict, computed_field
from pydantic_xml import BaseXmlModel, attr, element

from geekdo_sync.utils import NonEmptyStr, OptionalFromNonEmptyStr, OptionalNonEmptyStr

GeekdoUserId = NewType("GeekdoUserId", int)
"""Type alias for BoardGameGeek user IDs. To distinguish from other integers"""

GeekdoPlayId = NewType("GeekdoPlayId", int)
"""Type alias for BoardGameGeek play IDs. To distinguish from other integers"""

GeekdoItemId = NewType("GeekdoItemId", int)
"""Type alias for BoardGameGeek item IDs. To distinguish from other integers"""


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


def _parse_optional_user_id(val: Any) -> Optional[GeekdoUserId]:
    res = _parse_optional_id(val)
    if res is None:
        return None
    return GeekdoUserId(res)


def _parse_user_id(val: Any) -> GeekdoUserId:
    res = _parse_optional_id(val)
    if res is None:
        raise ValueError("UserId cannot be empty or zero")
    return GeekdoUserId(res)


def _parse_play_id(val: Any) -> GeekdoPlayId:
    res = _parse_optional_id(val)
    if res is None:
        raise ValueError("PlayId cannot be empty or zero")
    return GeekdoPlayId(res)


def _parse_item_id(val: Any) -> GeekdoItemId:
    res = _parse_optional_id(val)
    if res is None:
        raise ValueError("ItemId cannot be empty or zero")
    return GeekdoItemId(res)


class GeekdoSubtype(BaseXmlModel, tag="subtype"):
    value: str = attr()


class GeekdoSubtypes(BaseXmlModel, tag="subtypes"):
    subtype: List[GeekdoSubtype] = element(default_factory=list)


class GeekdoItem(BaseXmlModel, tag="item"):
    model_config = ConfigDict(populate_by_name=True)

    name: str = attr()
    objecttype: str = attr()
    objectid: Annotated[GeekdoItemId, BeforeValidator(_parse_item_id)] = attr()
    subtypes: GeekdoSubtypes = element()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def subtype(self) -> str:
        return self.subtypes.subtype[0].value if self.subtypes.subtype else ""


class GeekdoPlayer(BaseXmlModel, tag="player"):
    username: OptionalNonEmptyStr = attr(default=None)
    userid: Annotated[Optional[GeekdoUserId], BeforeValidator(_parse_optional_user_id)] = attr(default=None)
    name: NonEmptyStr = attr()
    startposition: OptionalNonEmptyStr = attr(default=None)
    color: OptionalNonEmptyStr = attr(default=None)
    score: OptionalFromNonEmptyStr[int] = attr(default=None)
    new: OptionalFromNonEmptyStr[bool] = attr(default=None)
    rating: OptionalFromNonEmptyStr[int] = attr(default=None)
    win: OptionalFromNonEmptyStr[bool] = attr(default=None)


class GeekdoPlayers(BaseXmlModel, tag="players"):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    player: List[GeekdoPlayer] = element(default_factory=list)


class GeekdoPlay(BaseXmlModel, tag="play"):
    """Play element in API response."""

    id: Annotated[GeekdoPlayId, BeforeValidator(_parse_play_id)] = attr()
    date: Date = attr()
    quantity: OptionalFromNonEmptyStr[int] = attr()
    length: OptionalFromNonEmptyStr[int] = attr()
    incomplete: OptionalFromNonEmptyStr[bool] = attr()
    nowinstats: OptionalFromNonEmptyStr[bool] = attr()
    location: OptionalNonEmptyStr = attr(default=None)
    item: GeekdoItem = element()
    comments: OptionalNonEmptyStr = element(default=None)
    players: Optional[GeekdoPlayers] = element(default=None)


class GeekdoPlaysResponse(BaseXmlModel, tag="plays"):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    username: NonEmptyStr = attr()
    userid: Annotated[GeekdoUserId, BeforeValidator(_parse_user_id)] = attr()
    total: int = attr()
    page: int = attr()
    play: List[GeekdoPlay] = element(default_factory=list)
