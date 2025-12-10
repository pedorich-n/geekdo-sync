from pydantic import ValidationError

from .schemas import APIPlaysResponse


def parse_plays_xml(xml_content: str) -> APIPlaysResponse:
    try:
        return APIPlaysResponse.from_xml(xml_content)
    except ValidationError as e:
        raise ValueError(f"Failed to validate plays data: {e}") from e
    except Exception as e:
        raise ValueError(f"Failed to parse XML: {e}") from e
