import logging

from app.domain.interface.logger import LoggerPort
from app.infrastructure.logging.context import request_id_ctx


class StandardLoggerAdapter(LoggerPort):
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def _extra(self, kwargs: dict) -> dict:
        return {"request_id": request_id_ctx.get(), **kwargs}

    def info(self, message: str, **kwargs) -> None:
        self._logger.info(message, extra=self._extra(kwargs))

    def error(self, message: str, **kwargs) -> None:
        self._logger.error(message, extra=self._extra(kwargs))

    def warning(self, message: str, **kwargs) -> None:
        self._logger.warning(message, extra=self._extra(kwargs))


def get_logger(name: str) -> StandardLoggerAdapter:
    return StandardLoggerAdapter(logging.getLogger(name))
