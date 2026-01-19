from typing import Annotated, Any, List, Optional

from annotated_types import MinLen
from pydantic import BeforeValidator


def _empty_str_to_none(v: Any) -> Optional[str]:
    if isinstance(v, str) and v.strip() == "":
        return None
    return v

type OptionalFromNonEmptyStr[X] = Annotated[Optional[X], BeforeValidator(_empty_str_to_none)]

type OptionalNonEmptyStr = Annotated[Optional[str], BeforeValidator(_empty_str_to_none)]

type NonEmptyStr = Annotated[str, MinLen(1)]

type NonEmptyList[T] = Annotated[List[T], MinLen(1)]