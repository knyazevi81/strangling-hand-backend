from typing import Annotated
import uuid

from fastapi import APIRouter, Depends

from app.application.use_cases.users import UserService
from app.presentation.fastapi.dependencies import get_user_service, get_current_user
from app.presentation.fastapi.schemas.schemas import (
    UserResponse,
    UsersListResponse,
    ChangePasswordRequest,
    MessageResponse,
)
from app.domain.models.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=UsersListResponse,
    summary="[Admin] Список всех пользователей",
)
async def get_all_users(
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UsersListResponse:
    users = await user_service.get_all_users(current_user)
    return UsersListResponse(
        users=[UserResponse(**u.model_dump()) for u in users],
        total=len(users),
    )


@router.get(
    "/pending",
    response_model=UsersListResponse,
    summary="[Admin] Пользователи, ожидающие активации",
)
async def get_pending_users(
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UsersListResponse:
    users = await user_service.get_pending_users(current_user)
    return UsersListResponse(
        users=[UserResponse(**u.model_dump()) for u in users],
        total=len(users),
    )


@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="[Admin] Активировать пользователя",
)
async def activate_user(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = await user_service.activate_user(user_id, current_user)
    return UserResponse(**user.model_dump())


@router.patch(
    "/change-password",
    response_model=MessageResponse,
    summary="[Admin] Сменить пароль пользователю",
)
async def change_password(
    body: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> MessageResponse:
    await user_service.change_password(body.user_id, body.new_password, current_user)
    return MessageResponse(message="Password changed successfully")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Профиль текущего пользователя",
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = await user_service.get_me(current_user.id)
    return UserResponse(**user.model_dump())
