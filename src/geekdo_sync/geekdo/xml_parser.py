from pydantic import ValidationError
from pydantic_xml.errors import BaseError

from .models import GeekdoPlaysResponse


def parse_plays_xml(xml_content: str) -> GeekdoPlaysResponse:
    try:
        return GeekdoPlaysResponse.from_xml(xml_content)
    except ValidationError as e:
        raise ValueError(f"Failed to validate plays data: {e}") from e
    except BaseError as e:
        raise ValueError(f"Failed to parse XML: {e}") from e
