import logging

from app.infrastructure.config.config import get_settings

config = get_settings()


def configure_logging() -> None:
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format=config.LOGGING_FORMAT,
        datefmt=config.LOGGING_DATEFMT,
    )
