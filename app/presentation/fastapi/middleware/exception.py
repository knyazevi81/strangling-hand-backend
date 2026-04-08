from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import JSONResponse

import http

from app.domain.logger.interface import LoggerPort
from app.domain.exceptions.base import AppException

class ExceptionMiddleware:
    """
    Миддлварь для request_id
    """
    def __init__(self, app: ASGIApp, logger: LoggerPort) -> None:
        self.app = app
        self._logger = logger
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            await self.app(scope, receive, send)
            return
        
        if scope["type"] != 'http':
            await self.app(scope, receive, send)
            return
        
        try:
            await self.app(scope, receive, send)
        
        except AppException as exc:
            self._logger.warning(
                "Unhandeled exception",
                error=str(exc),
                error_type=type(exc).__name__,
                path=scope.get("path"),
                method=scope.get("method")
            )
            response = JSONResponse(
                status_code=exc.code,
                content={
                    "result": {
                        "error": exc.message,
                    }
                }
            )
            await response(scope, receive, send)
            
        except Exception as exc:
            raise exc
            self._logger.error(
                "Unhandeled exception",
                error=str(exc),
                error_type=type(exc).__name__,
                path=scope.get("path"),
                method=scope.get("method")
            )
            response = JSONResponse(
                status_code=http.HTTPStatus.BAD_REQUEST,
                content={
                    "error": "Notification Error",
                }
            )
            await response(scope, receive, send)