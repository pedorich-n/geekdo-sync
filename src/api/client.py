import logging
from time import sleep

import requests

from .schemas import APIPlaysResponse
from .xml_parser import parse_plays_xml

logger = logging.getLogger(__name__)

BGG_API_BASE_URL = "https://boardgamegeek.com/xmlapi2"


class BGGClient:
    """Client for fetching play data from BoardGameGeek API."""

    def __init__(self, api_key: str, base_url: str = BGG_API_BASE_URL, timeout: int = 30, delay: float = 1.0):
        """
        Initialize BGG client.

        Args:
            api_key: BGG API token/key for authentication
            base_url: Base URL for BGG API (default: official API)
            timeout: Request timeout in seconds (default: 30)
            delay: Delay in seconds between API requests (default: 1.0)
        """
        self.base_url = base_url
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def get_plays(self, username: str, page: int = 1) -> APIPlaysResponse:
        """
        Fetch a page of plays for a user.

        Args:
            username: BGG username to fetch plays for
            page: Page number to fetch (default: 1, 100 records per page)

        Returns:
            APIPlaysResponse containing plays for the requested page

        Raises:
            ValueError: If API request fails or XML parsing fails
        """
        url = f"{BGG_API_BASE_URL}/plays"
        params: dict[str, str] = {
            "username": username,
            "page": str(page),
        }

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

    def get_all_plays(self, username: str) -> list[APIPlaysResponse]:
        """
        Fetch all plays for a user across all pages.

        Args:
            username: BGG username to fetch plays for

        Returns:
            List of APIPlaysResponse objects, one per page

        Raises:
            ValueError: If any API request or parsing fails
        """
        all_responses: list[APIPlaysResponse] = []
        page = 1

        while True:
            logger.info(f"Fetching page {page}")
            response = self.get_plays(username=username, page=page)
            all_responses.append(response)

            # Check if we've reached the last page
            if len(response.play) < 100:
                logger.info(f"Finished fetching all pages ({response.total} total plays)")
                break

            sleep(self.delay)
            page += 1

        return all_responses

    def close(self) -> None:
        """Close the client session."""
        self.session.close()

    def __enter__(self) -> "BGGClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
