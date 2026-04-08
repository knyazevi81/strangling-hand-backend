import logging

from app.domain.interface.logger import LoggerPort

class LoggerAdapter(LoggerPort):
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        
    def info(self, message: str, **kwargs) -> None:
        self._logger.info(message, extra=kwargs)

    def error(self, message: str, **kwargs) -> None:
        self._logger.error(message, extra=kwargs)

    def warning(self, message: str, **kwargs) -> None:
        self._logger.warning(message, extra=kwargs)
        
def get_logger(name: str):
    return LoggerAdapter(logging.getLogger(name))