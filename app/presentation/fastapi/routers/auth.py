from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.use_cases.auth import AuthService
from app.presentation.fastapi.dependencies import get_auth_service
from app.presentation.fastapi.schemas.schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UserResponse,
    MessageResponse,
)
from app.domain.models.models import User
from app.presentation.fastapi.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    body: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    user = await auth_service.register(body.email, body.password)
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    pair = await auth_service.login(body.email, body.password)
    return TokenResponse(**pair.model_dump())


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    pair = await auth_service.refresh(body.refresh_token)
    return TokenResponse(**pair.model_dump())


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    _: Annotated[User, Depends(get_current_user)],
) -> MessageResponse:
    # Stateless JWT — клиент удаляет токен на своей стороне
    return MessageResponse(message="Successfully logged out")
