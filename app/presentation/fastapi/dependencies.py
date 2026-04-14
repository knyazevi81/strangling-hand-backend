from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.infrastructure.database.dependencies import get_uow
from app.infrastructure.database.uow import UnitOfWork
from app.infrastructure.config.config import get_settings, Settings
from app.infrastructure.security.jwt import JoseTokenService
from app.infrastructure.security.password import BcryptPasswordHasher
from app.infrastructure.email.service import EmailService
from app.application.use_cases.auth import AuthService
from app.application.use_cases.users import UserService
from app.application.use_cases.subscribes import SubscribeService
from app.domain.models.models import User
from app.domain.exceptions.base import NotAuthenticatedError

bearer_scheme = HTTPBearer(auto_error=False)


def get_password_hasher() -> BcryptPasswordHasher:
    return BcryptPasswordHasher()


def get_token_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> JoseTokenService:
    return JoseTokenService(settings)


def get_email_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> EmailService:
    return EmailService(settings)


def get_auth_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    password_hasher: Annotated[BcryptPasswordHasher, Depends(get_password_hasher)],
    token_service: Annotated[JoseTokenService, Depends(get_token_service)],
) -> AuthService:
    return AuthService(uow, password_hasher, token_service)


def get_user_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    password_hasher: Annotated[BcryptPasswordHasher, Depends(get_password_hasher)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> UserService:
    return UserService(uow, password_hasher, email_service)


def get_subscribe_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> SubscribeService:
    return SubscribeService(uow, email_service)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    if credentials is None:
        raise NotAuthenticatedError()
    return await auth_service.get_current_user(credentials.credentials)


async def get_uow_with_articles(
    session=Depends(lambda: None),
):
    from app.infrastructure.database.engine import async_session_maker
    from app.infrastructure.database.uow import UnitOfWorkWithArticles
    async with async_session_maker() as s:
        async with UnitOfWorkWithArticles(s) as uow:
            yield uow
