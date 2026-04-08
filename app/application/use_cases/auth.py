import uuid

from app.infrastructure.database.uow import UnitOfWork
from app.infrastructure.security.jwt import JoseTokenService
from app.infrastructure.security.password import BcryptPasswordHasher
from app.domain.models.models import TokenPair, User
from app.domain.exceptions.base import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserInactiveError,
    UserNotFoundError,
)


class AuthService:

    def __init__(
        self,
        uow: UnitOfWork,
        password_hasher: BcryptPasswordHasher,
        token_service: JoseTokenService,
    ) -> None:
        self.uow = uow
        self.password_hasher = password_hasher
        self.token_service = token_service

    async def register(self, email: str, password: str) -> User:
        existing = await self.uow.users.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError()

        hashed = self.password_hasher.hash(password)
        user_id = uuid.uuid4()

        await self.uow.users.add(
            id=user_id,
            email=email,
            hashed_password=hashed,
            is_active=False,        # деактивирован до подтверждения админом
            is_superuser=False,
        )

        return User(
            id=user_id,
            email=email,
            is_active=False,
            is_superuser=False,
        )

    async def login(self, email: str, password: str) -> TokenPair:
        user = await self.uow.users.get_by_email(email)
        if not user:
            raise InvalidCredentialsError()

        hashed_password = await self.uow.users.get_hashed_password(email)
        if not self.password_hasher.verify(password, hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise UserInactiveError()

        return self.token_service.create_pair(str(user.id))

    async def refresh(self, refresh_token: str) -> TokenPair:
        payload = self.token_service.decode_refresh(refresh_token)
        return self.token_service.create_pair(payload.sub)

    async def get_current_user(self, access_token: str) -> User:
        payload = self.token_service.decode_access(access_token)
        user = await self.uow.users.get_by_id(uuid.UUID(payload.sub))
        if not user:
            raise UserNotFoundError()
        if not user.is_active:
            raise UserInactiveError()
        return user
