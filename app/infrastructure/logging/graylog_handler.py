import pygelf
import logging

class GrayLogGelfHandler(logging.Handler):
    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self._handler = pygelf.GelfTcpHandler(
            host=host,
            port=port
        )
    
    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._handler.emit(record)
        except Exception:
            self.handleError(record)