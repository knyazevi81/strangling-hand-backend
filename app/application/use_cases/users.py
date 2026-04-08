import uuid

from app.infrastructure.database.uow import UnitOfWork
from app.infrastructure.security.password import BcryptPasswordHasher
from app.domain.models.models import User
from app.domain.exceptions.base import UserNotFoundError, ForbiddenError


class UserService:

    def __init__(
        self,
        uow: UnitOfWork,
        password_hasher: BcryptPasswordHasher,
    ) -> None:
        self.uow = uow
        self.password_hasher = password_hasher

    async def get_all_users(self, current_user: User) -> list[User]:
        if not current_user.is_superuser:
            raise ForbiddenError()
        return await self.uow.users.find_all()

    async def get_pending_users(self, current_user: User) -> list[User]:
        """Пользователи, ожидающие активации (is_active=False)."""
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

        return User(
            id=user.id,
            email=user.email,
            is_active=True,
            is_superuser=user.is_superuser,
        )

    async def change_password(
        self,
        user_id: uuid.UUID,
        new_password: str,
        current_user: User,
    ) -> None:
        if not current_user.is_superuser:
            raise ForbiddenError()

        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        hashed = self.password_hasher.hash(new_password)
        await self.uow.users.change_password(user_id, hashed)

    async def get_me(self, user_id: uuid.UUID) -> User:
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user
