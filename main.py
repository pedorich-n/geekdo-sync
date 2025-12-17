"""Main entry point for GeekDo sync."""

import logging
import os
import sys
from datetime import datetime

from pygrister.api import GristApi  # type: ignore[import-untyped]

from src.geekdo.client import BGGClient
from src.sync import GristSync

"""Configure logging for the application."""
logging.basicConfig(
    level=logging.DEBUG,
    format="[{asctime}] [{levelname:<5s}] [{name:<20.20}] [{funcName:<20.20}] - {message}",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    style="{",
)

# Quiet down noisy libraries
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)


def main() -> int:
    """Run the sync process."""

    logger.info("=" * 60)
    logger.info("Starting GeekDo Sync")
    logger.info("=" * 60)

    # Load configuration from environment
    geekdo_username = os.getenv("GEEKDO_USERNAME")
    geekdo_token = os.getenv("GEEKDO_TOKEN")
    grist_doc_id = os.getenv("GRIST_DOC_ID")

    # Validate required environment variables
    missing_vars = []
    if not geekdo_username:
        missing_vars.append("GEEKDO_USERNAME")
    if not geekdo_token:
        missing_vars.append("GEEKDO_TOKEN")
    if not grist_doc_id:
        missing_vars.append("GRIST_DOC_ID")

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set them in your .env file or environment")
        return 1

    logger.info("Configuration:")
    logger.info(f"  GeekDo Username: {geekdo_username}")
    logger.info(f"  Grist Document ID: {grist_doc_id}")

    try:
        # Initialize clients
        logger.info("Initializing clients...")
        bgg_client = BGGClient(api_key=geekdo_token)  # type: ignore[arg-type]
        grist_api = GristApi()

        # Initialize sync orchestrator
        sync = GristSync(
            bgg_client=bgg_client,
            bgg_username=geekdo_username,  # type: ignore[arg-type]
            grist_client=grist_api,
            grist_doc_id=grist_doc_id,  # type: ignore[arg-type]
        )

        # Run the sync
        start_time = datetime.now()
        success = sync.run_sync()
        elapsed = datetime.now() - start_time

        if success:
            logger.info("=" * 60)
            logger.info(f"Sync completed successfully in {elapsed.total_seconds():.2f} seconds")
            logger.info("=" * 60)
            return 0
        else:
            logger.error("=" * 60)
            logger.error("Sync failed")
            logger.error("=" * 60)
            return 1

    except KeyboardInterrupt:
        logger.warning("Sync interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Fatal error during sync: {e}", exc_info=True)
        return 1
    finally:
        # Cleanup
        if "bgg_client" in locals():
            bgg_client.close()


if __name__ == "__main__":
    sys.exit(main())
