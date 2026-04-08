import uuid

from app.infrastructure.database.uow import UnitOfWork
from app.domain.models.models import Subscribe, User
from app.domain.exceptions.base import (
    SubscribeNotFoundError,
    ForbiddenError,
    UserNotFoundError,
)


def _render_payload(template: str, ip: str, port: str) -> str:
    """Подставляет {ip} и {port} в payload шаблон."""
    return template.replace("{ip}", ip).replace("{port}", port)


class SubscribeService:

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    # ── Admin ──────────────────────────────────────────────────────────────

    async def get_all(self, current_user: User) -> list[Subscribe]:
        if not current_user.is_superuser:
            raise ForbiddenError()
        subs = await self.uow.subscribes.find_all()
        return [
            Subscribe(
                id=s.id,
                user_id=s.user_id,
                ip=s.ip,
                port=s.port,
                payload=_render_payload(s.payload, s.ip, s.port),
            )
            for s in subs
        ]

    async def get_by_user_id(
        self, user_id: uuid.UUID, current_user: User
    ) -> list[Subscribe]:
        if not current_user.is_superuser:
            raise ForbiddenError()
        subs = await self.uow.subscribes.find_by_user_id(user_id)
        return [
            Subscribe(
                id=s.id,
                user_id=s.user_id,
                ip=s.ip,
                port=s.port,
                payload=_render_payload(s.payload, s.ip, s.port),
            )
            for s in subs
        ]

    async def create(
        self,
        user_id: uuid.UUID,
        ip: str,
        port: str,
        payload_template: str,
        current_user: User,
    ) -> Subscribe:
        if not current_user.is_superuser:
            raise ForbiddenError()

        # Проверяем что юзер существует
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        subscribe_id = uuid.uuid4()

        await self.uow.subscribes.add(
            id=subscribe_id,
            user_id=user_id,
            ip=ip,
            port=port,
            payload=payload_template,   # храним шаблон, рендерим при выдаче
        )

        return Subscribe(
            id=subscribe_id,
            user_id=user_id,
            ip=ip,
            port=port,
            payload=_render_payload(payload_template, ip, port),
        )

    async def update(
        self,
        subscribe_id: uuid.UUID,
        current_user: User,
        ip: str | None = None,
        port: str | None = None,
        payload_template: str | None = None,
    ) -> Subscribe:
        if not current_user.is_superuser:
            raise ForbiddenError()

        sub = await self.uow.subscribes.get_by_id(subscribe_id)
        if not sub:
            raise SubscribeNotFoundError()

        updates: dict = {}
        if ip is not None:
            updates["ip"] = ip
        if port is not None:
            updates["port"] = port
        if payload_template is not None:
            updates["payload"] = payload_template

        if updates:
            await self.uow.subscribes.update(subscribe_id, **updates)

        # обновляем локальную копию для ответа
        final_ip = ip or sub.ip
        final_port = port or sub.port
        final_template = payload_template or sub.payload

        return Subscribe(
            id=sub.id,
            user_id=sub.user_id,
            ip=final_ip,
            port=final_port,
            payload=_render_payload(final_template, final_ip, final_port),
        )

    async def delete(self, subscribe_id: uuid.UUID, current_user: User) -> None:
        if not current_user.is_superuser:
            raise ForbiddenError()

        sub = await self.uow.subscribes.get_by_id(subscribe_id)
        if not sub:
            raise SubscribeNotFoundError()

        await self.uow.subscribes.delete(subscribe_id)

    # ── User (только свои подписки) ────────────────────────────────────────

    async def get_my_subscribes(self, current_user: User) -> list[Subscribe]:
        """Возвращает активные подписки текущего юзера с подставленным payload."""
        subs = await self.uow.subscribes.find_by_user_id(current_user.id)
        return [
            Subscribe(
                id=s.id,
                user_id=s.user_id,
                ip=s.ip,
                port=s.port,
                payload=_render_payload(s.payload, s.ip, s.port),
            )
            for s in subs
        ]
