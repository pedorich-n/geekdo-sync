import logging
from datetime import date
from typing import Optional

import requests
from pydantic import SecretStr

from .models import APIPlaysResponse
from .xml_parser import parse_plays_xml

logger = logging.getLogger(__name__)

BGG_API_BASE_URL = "https://boardgamegeek.com/xmlapi2"


class BGGClient:
    def __init__(self, api_key: SecretStr, base_url: str = BGG_API_BASE_URL, timeout: int = 30, delay: float = 1.0):
        self.base_url = base_url
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key.get_secret_value()}"})

    def get_plays(
        self,
        username: str,
        page: int = 1,
        mindate: Optional[date] = None,
        maxdate: Optional[date] = None,
    ) -> APIPlaysResponse:
        url = f"{BGG_API_BASE_URL}/plays"
        params: dict[str, str] = {
            "username": username,
            "page": str(page),
        }

        if mindate:
            params["mindate"] = mindate.isoformat()
        if maxdate:
            params["maxdate"] = maxdate.isoformat()

        logger.debug(f"Fetching plays for {username}, page {page}")

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch plays from BGG API: {e}")
            raise ValueError(f"Failed to fetch plays from BGG API: {e}") from e

        try:
            parsed_response = parse_plays_xml(response.text)
            logger.debug(f"Successfully parsed {len(parsed_response.play)} plays from page {page}")
            return parsed_response
        except ValueError as e:
            logger.error(f"Failed to parse BGG API response: {e}")
            raise

    def __enter__(self) -> "BGGClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.session.close()
