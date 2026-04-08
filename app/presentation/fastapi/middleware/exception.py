from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import JSONResponse

import http

from app.domain.interface.logger import LoggerPort
from app.domain.exceptions.base import AppException


class ExceptionMiddleware:
    """
    Миддлварь для обработки доменных исключений.
    """
    def __init__(self, app: ASGIApp, logger: LoggerPort) -> None:
        self.app = app
        self._logger = logger

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            await self.app(scope, receive, send)
            return

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)

        except AppException as exc:
            self._logger.warning(
                "App exception",
                error=str(exc),
                error_type=type(exc).__name__,
                path=scope.get("path"),
            )
            response = JSONResponse(
                status_code=exc.code,
                content={
                    "result": {
                        "error": exc.message,
                    }
                },
            )
            await response(scope, receive, send)

        except Exception as exc:
            self._logger.error(
                "Unhandled exception",
                error=str(exc),
                error_type=type(exc).__name__,
                path=scope.get("path"),
            )
            response = JSONResponse(
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                content={
                    "result": {
                        "error": "Internal server error",
                    }
                },
            )
            await response(scope, receive, send)
