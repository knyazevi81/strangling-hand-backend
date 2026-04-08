from typing import Annotated
import uuid

from fastapi import APIRouter, Depends

from app.application.use_cases.subscribes import SubscribeService
from app.presentation.fastapi.dependencies import get_subscribe_service, get_current_user
from app.presentation.fastapi.schemas.schemas import (
    SubscribeResponse,
    SubscribesListResponse,
    CreateSubscribeRequest,
    UpdateSubscribeRequest,
    MessageResponse,
)
from app.domain.models.models import User

router = APIRouter(prefix="/subscribes", tags=["subscribes"])


# ── User endpoints ─────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=SubscribesListResponse,
    summary="Мои VPN подписки (с готовым payload для подключения)",
)
async def get_my_subscribes(
    current_user: Annotated[User, Depends(get_current_user)],
    subscribe_service: Annotated[SubscribeService, Depends(get_subscribe_service)],
) -> SubscribesListResponse:
    subs = await subscribe_service.get_my_subscribes(current_user)
    return SubscribesListResponse(
        subscribes=[SubscribeResponse(**s.model_dump()) for s in subs],
        total=len(subs),
    )


# ── Admin endpoints ────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=SubscribesListResponse,
    summary="[Admin] Все подписки",
)
async def get_all_subscribes(
    current_user: Annotated[User, Depends(get_current_user)],
    subscribe_service: Annotated[SubscribeService, Depends(get_subscribe_service)],
) -> SubscribesListResponse:
    subs = await subscribe_service.get_all(current_user)
    return SubscribesListResponse(
        subscribes=[SubscribeResponse(**s.model_dump()) for s in subs],
        total=len(subs),
    )


@router.get(
    "/user/{user_id}",
    response_model=SubscribesListResponse,
    summary="[Admin] Подписки конкретного пользователя",
)
async def get_subscribes_by_user(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    subscribe_service: Annotated[SubscribeService, Depends(get_subscribe_service)],
) -> SubscribesListResponse:
    subs = await subscribe_service.get_by_user_id(user_id, current_user)
    return SubscribesListResponse(
        subscribes=[SubscribeResponse(**s.model_dump()) for s in subs],
        total=len(subs),
    )


@router.post(
    "/",
    response_model=SubscribeResponse,
    status_code=201,
    summary="[Admin] Выдать подписку пользователю",
)
async def create_subscribe(
    body: CreateSubscribeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    subscribe_service: Annotated[SubscribeService, Depends(get_subscribe_service)],
) -> SubscribeResponse:
    sub = await subscribe_service.create(
        user_id=body.user_id,
        ip=body.ip,
        port=body.port,
        payload_template=body.payload_template,
        current_user=current_user,
    )
    return SubscribeResponse(**sub.model_dump())


@router.patch(
    "/{subscribe_id}",
    response_model=SubscribeResponse,
    summary="[Admin] Обновить подписку",
)
async def update_subscribe(
    subscribe_id: uuid.UUID,
    body: UpdateSubscribeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    subscribe_service: Annotated[SubscribeService, Depends(get_subscribe_service)],
) -> SubscribeResponse:
    sub = await subscribe_service.update(
        subscribe_id=subscribe_id,
        current_user=current_user,
        ip=body.ip,
        port=body.port,
        payload_template=body.payload_template,
    )
    return SubscribeResponse(**sub.model_dump())


@router.delete(
    "/{subscribe_id}",
    response_model=MessageResponse,
    summary="[Admin] Удалить подписку",
)
async def delete_subscribe(
    subscribe_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    subscribe_service: Annotated[SubscribeService, Depends(get_subscribe_service)],
) -> MessageResponse:
    await subscribe_service.delete(subscribe_id, current_user)
    return MessageResponse(message="Subscribe deleted successfully")
