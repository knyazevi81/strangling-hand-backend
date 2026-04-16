"""
WebSocket прокси — бэкенд получает ключи пользователя,
передаёт их в ping-service и стримит результаты обратно на фронт.
"""
import json
from typing import Annotated

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx

from app.infrastructure.database.dependencies import get_uow
from app.infrastructure.database.uow import UnitOfWork
from app.infrastructure.config.config import get_settings, Settings
from app.infrastructure.security.jwt import JoseTokenService
from app.infrastructure.security.password import BcryptPasswordHasher
from app.application.use_cases.auth import AuthService
from app.domain.models.models import User
from app.domain.exceptions.base import NotAuthenticatedError, UserInactiveError

router = APIRouter(prefix="/ping", tags=["ping"])

PING_SERVICE_WS = "ws://host.docker.internal:8088/ws/ping"


async def _get_user_from_token(token: str, uow: UnitOfWork, settings: Settings) -> User:
    """Валидация JWT токена для WebSocket (header не поддерживается в WS)."""
    token_service = JoseTokenService(settings)
    hasher = BcryptPasswordHasher()
    auth_service = AuthService(uow, hasher, token_service)
    return await auth_service.get_current_user(token)


@router.websocket("/ws")
async def ping_ws(websocket: WebSocket) -> None:
    """
    WebSocket прокси для пинга личных подключений пользователя.

    Фронт отправляет токен первым сообщением:
    {"token": "eyJ..."}

    Затем бэкенд получает ключи пользователя из БД и отправляет
    их в ping-service. Результаты стримятся обратно по мере готовности.

    Формат результата от ping-service (пробрасывается как есть):
    {"uri": "...", "status": "ok", "avg_ms": 42, ...}
    {"done": true, "total": 3}
    """
    await websocket.accept()

    async with get_uow_ws() as uow:
        settings = get_settings()

        # 1. Аутентификация — токен первым сообщением
        try:
            auth_raw = await websocket.receive_text()
            auth_data = json.loads(auth_raw)
            token = auth_data.get("token", "")
        except Exception:
            await websocket.send_text(json.dumps({"error": "Невалидный запрос авторизации"}))
            await websocket.close(code=1008)
            return

        try:
            user = await _get_user_from_token(token, uow, settings)
        except (NotAuthenticatedError, UserInactiveError, Exception) as e:
            await websocket.send_text(json.dumps({"error": "Не авторизован"}))
            await websocket.close(code=1008)
            return

        # 2. Получаем личные подключения пользователя из БД
        subscribes = await uow.subscribes.find_by_user_id(user.id)

        if not subscribes:
            await websocket.send_text(json.dumps({"error": "Нет подключений для пинга"}))
            await websocket.close()
            return

        # Из payload извлекаем реальный vless:// URI
        # payload хранится как шаблон с {ip} и {port}
        uris = []
        for sub in subscribes:
            rendered = sub.payload.replace("{ip}", sub.ip).replace("{port}", sub.port)
            uris.append(rendered)

        # 3. Отправляем в ping-service и проксируем ответ
        ping_request = json.dumps({
            "keys": uris,
            "count": 3,
            "timeout": 8.0,
            "concurrency": 3,
        })

        try:
            async with httpx.AsyncClient() as http_client:
                async with http_client.stream("GET", PING_SERVICE_WS) as _:
                    pass
        except Exception:
            pass

        # Используем websockets напрямую для соединения с ping-service
        try:
            import websockets

            async with websockets.connect(PING_SERVICE_WS) as ping_ws:
                # Отправляем запрос в ping-service
                await ping_ws.send(ping_request)

                # Проксируем ответы на фронт
                async for message in ping_ws:
                    try:
                        await websocket.send_text(message)
                        # Если это сигнал done — закрываем
                        data = json.loads(message)
                        if data.get("done"):
                            break
                    except WebSocketDisconnect:
                        break
                    except Exception:
                        break

        except WebSocketDisconnect:
            pass
        except Exception as e:
            try:
                await websocket.send_text(json.dumps({"error": f"Ping service недоступен: {e}"}))
            except Exception:
                pass
        finally:
            try:
                await websocket.close()
            except Exception:
                pass


# ── Вспомогательная функция для UoW в WebSocket контексте ─────────────────────

from contextlib import asynccontextmanager
from app.infrastructure.database.engine import async_session_maker
from app.infrastructure.database.uow import UnitOfWork


@asynccontextmanager
async def get_uow_ws():
    async with async_session_maker() as session:
        async with UnitOfWork(session) as uow:
            yield uow
