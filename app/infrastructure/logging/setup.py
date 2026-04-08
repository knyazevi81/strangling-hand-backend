import logging
import sys

from app.infrastructure.config.config import get_settings
from app.infrastructure.logging.filters import RequestContextFilter
from app.infrastructure.logging.graylog_handler import GrayLogGelfHandler

settings = get_settings()

def configure_logging() -> None:
    root = logging.getLogger()
    root.setLevel(level=settings.LOG_LEVEL)
    
    # настройка стдаут логгера
    formatter = logging.Formatter(
        settings.LOGGING_FORMAT,
        settings.LOGGING_DATEFMT
    )
    
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.addFilter(RequestContextFilter())
    
    root.handlers.clear()
    root.addHandler(stdout_handler)
    
    if settings.GRAYLOG_ENABLED:
        # настройка стдаут логгера
        graylog_handler = GrayLogGelfHandler(
            settings.GRAYLOG_HOST,
            settings.GRAYLOG_PORT
        )
        graylog_handler.setFormatter(formatter)
        graylog_handler.addFilter(RequestContextFilter())
        root.addHandler(graylog_handler)
