import logging

from utils.config import getConfig


def configure_logging() -> None:
    """Configure root logging once for the backend."""
    cfg = getConfig(validate=False)
    level_name = cfg.get_log_level().upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
