import logging
import sys
from datetime import datetime

from pygrister.api import GristApi  # type: ignore[import-untyped]

from src.config import Config
from src.geekdo.client import BGGClient
from src.sync import GristSync

logging.basicConfig(
    level=logging.DEBUG,
    format="[{asctime}] [{levelname:<5s}] - {message}",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    style="{",
)

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)


def main() -> int:
    """Run the sync process."""

    try:
        config = Config()  # type: ignore[call-arg]
    except Exception as e:
        logger.error(f"Error loading configuration: {e}", exc_info=True)
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("Starting GeekDo Sync")
    logger.info("=" * 60)

    logger.info("Configuration:")
    logger.info(f"  GeekDo Username: {config.geekdo.username}")
    logger.info(f"  Grist Document ID: {config.grist.doc_id}")

    try:
        # Initialize clients
        logger.info("Initializing clients...")
        with BGGClient(api_key=config.geekdo.token) as bgg_client:  # type: ignore[arg-type]
            grist_api = GristApi()

            # Initialize sync orchestrator
            sync = GristSync(
                bgg_client=bgg_client,
                bgg_username=config.geekdo.username,
                grist_client=grist_api,
                grist_doc_id=config.grist.doc_id,
            )

            # Run the sync
            start_time = datetime.now()
            success = sync.run_sync()
            elapsed = datetime.now() - start_time

            if success:
                logger.info("=" * 60)
                logger.info(f"Sync completed successfully in {elapsed.total_seconds():.2f} seconds")
                logger.info("=" * 60)
                sys.exit(0)
            else:
                logger.error("=" * 60)
                logger.error("Sync failed")
                logger.error("=" * 60)
                sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("Sync interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error during sync: {e}", exc_info=True)
        sys.exit(1)
