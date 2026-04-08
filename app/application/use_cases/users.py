import uuid

from app.infrastructure.database.uow import UnitOfWork
from app.infrastructure.security.password import BcryptPasswordHasher
from app.infrastructure.email.service import EmailService
from app.domain.models.models import User
from app.domain.exceptions.base import (
    UserNotFoundError,
    ForbiddenError,
    InvalidCredentialsError,
)


class UserService:

    def __init__(
        self,
        uow: UnitOfWork,
        password_hasher: BcryptPasswordHasher,
        email_service: EmailService,
    ) -> None:
        self.uow = uow
        self.password_hasher = password_hasher
        self.email_service = email_service

    async def get_all_users(self, current_user: User) -> list[User]:
        if not current_user.is_superuser:
            raise ForbiddenError()
        return await self.uow.users.find_all()

    async def get_pending_users(self, current_user: User) -> list[User]:
        if not current_user.is_superuser:
            raise ForbiddenError()
        return await self.uow.users.find_all(is_active=False)

    async def activate_user(self, user_id: uuid.UUID, current_user: User) -> User:
        if not current_user.is_superuser:
            raise ForbiddenError()

        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        await self.uow.users.activate(user_id)
        await self.email_service.send_account_activated(user.email)

        return User(id=user.id, email=user.email, is_active=True, is_superuser=user.is_superuser)

    # ── Admin меняет пароль любому ─────────────────────────────────────────

    async def admin_change_password(self, user_id: uuid.UUID, new_password: str,
                                    current_user: User) -> None:
        if not current_user.is_superuser:
            raise ForbiddenError()

        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        hashed = self.password_hasher.hash(new_password)
        await self.uow.users.change_password(user_id, hashed)
        await self.email_service.send_password_changed(user.email)

    # ── Пользователь меняет свой пароль ───────────────────────────────────

    async def change_my_password(self, current_user: User,
                                  old_password: str, new_password: str) -> None:
        hashed_password = await self.uow.users.get_hashed_password(current_user.email)
        if not self.password_hasher.verify(old_password, hashed_password):
            raise InvalidCredentialsError("Неверный текущий пароль")

        new_hashed = self.password_hasher.hash(new_password)
        await self.uow.users.change_password(current_user.id, new_hashed)
        await self.email_service.send_password_changed(current_user.email)

    async def get_me(self, user_id: uuid.UUID) -> User:
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    # ── Рассылка от админа ────────────────────────────────────────────────

    async def send_notification_to_all(self, subject: str, message: str,
                                        current_user: User) -> int:
        if not current_user.is_superuser:
            raise ForbiddenError()

        all_users = await self.uow.users.find_all(is_active=True)
        emails = [u.email for u in all_users if not u.is_superuser]
        if emails:
            await self.email_service.send_custom(emails, subject, message)
        return len(emails)

    async def send_notification_to_user(self, user_id: uuid.UUID, subject: str,
                                         message: str, current_user: User) -> None:
        if not current_user.is_superuser:
            raise ForbiddenError()

        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        await self.email_service.send_custom(user.email, subject, message)
