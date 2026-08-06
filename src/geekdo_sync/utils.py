from typing import Annotated, Any

from annotated_types import MinLen
from pydantic import BeforeValidator


def _empty_str_to_none(v: Any) -> str | None:
    if isinstance(v, str) and v.strip() == "":
        return None
    return v


type OptionalFromNonEmptyStr[X] = Annotated[X | None, BeforeValidator(_empty_str_to_none)]

type OptionalNonEmptyStr = Annotated[str | None, BeforeValidator(_empty_str_to_none)]

type NonEmptyStr = Annotated[str, MinLen(1)]

type NonEmptyList[T] = Annotated[list[T], MinLen(1)]
