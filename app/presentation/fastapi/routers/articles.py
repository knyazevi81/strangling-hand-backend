import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi.responses import Response

from app.application.use_cases.articles import ArticleService
from app.domain.models.models import User
from app.domain.exceptions.base import AppException
from app.presentation.fastapi.dependencies import get_current_user, get_uow_with_articles
from app.presentation.fastapi.schemas.articles import (
    ArticleListItemResponse, ArticleDetailResponse,
    CreateDraftResponse, UpdateArticleRequest,
    LikeResponse, CommentResponse, AddCommentRequest,
    ImageUploadResponse,
)

router = APIRouter(tags=["articles"])


def get_article_service(uow=Depends(get_uow_with_articles)) -> ArticleService:
    return ArticleService(uow)


# ── Articles ───────────────────────────────────────────────────────────────────

@router.get("/articles/", response_model=list[ArticleListItemResponse])
async def list_articles(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ArticleService, Depends(get_article_service)],
    search: str | None = Query(default=None),
    tag: str | None = Query(default=None),
) -> list[ArticleListItemResponse]:
    items = await service.get_list(current_user, search, tag)
    return [ArticleListItemResponse(**i.model_dump()) for i in items]


@router.get("/articles/{article_id}", response_model=ArticleDetailResponse)
async def get_article(
    article_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ArticleService, Depends(get_article_service)],
) -> ArticleDetailResponse:
    detail = await service.get_detail(article_id, current_user)
    return ArticleDetailResponse(**detail.model_dump())


@router.post("/articles/", response_model=CreateDraftResponse, status_code=201)
async def create_draft(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ArticleService, Depends(get_article_service)],
) -> CreateDraftResponse:
    result = await service.create_draft(current_user)
    return CreateDraftResponse(**result)


@router.put("/articles/{article_id}", response_model=dict)
async def update_article(
    article_id: uuid.UUID,
    body: UpdateArticleRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ArticleService, Depends(get_article_service)],
) -> dict:
    await service.update(
        article_id, current_user,
        title=body.title, content=body.content,
        tags=body.tags, status=body.status,
    )
    return {"message": "Обновлено"}


@router.delete("/articles/{article_id}", response_model=dict)
async def delete_article(
    article_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ArticleService, Depends(get_article_service)],
) -> dict:
    await service.delete(article_id, current_user)
    return {"message": "Удалено"}


# ── Images ─────────────────────────────────────────────────────────────────────

@router.post("/articles/{article_id}/images", response_model=ImageUploadResponse)
async def upload_image(
    article_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ArticleService, Depends(get_article_service)],
    file: UploadFile = File(...),
) -> ImageUploadResponse:
    data = await file.read()
    result = await service.upload_image(
        article_id, current_user,
        data=data,
        mime_type=file.content_type or "image/jpeg",
        filename=file.filename or "image",
    )
    return ImageUploadResponse(**result)


@router.get("/images/{image_id}")
async def get_image(
    image_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ArticleService, Depends(get_article_service)],
) -> Response:
    data, mime_type = await service.get_image(image_id)
    return Response(
        content=data,
        media_type=mime_type,
        headers={"Cache-Control": "max-age=86400"},
    )


# ── Likes ──────────────────────────────────────────────────────────────────────

@router.post("/articles/{article_id}/like", response_model=LikeResponse)
async def toggle_like(
    article_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ArticleService, Depends(get_article_service)],
) -> LikeResponse:
    result = await service.toggle_like(article_id, current_user)
    return LikeResponse(**result)


# ── Comments ───────────────────────────────────────────────────────────────────

@router.get("/articles/{article_id}/comments", response_model=list[CommentResponse])
async def get_comments(
    article_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ArticleService, Depends(get_article_service)],
) -> list[CommentResponse]:
    comments = await service.get_comments(article_id, current_user)
    return [CommentResponse(**c.model_dump()) for c in comments]


@router.post("/articles/{article_id}/comments", response_model=CommentResponse, status_code=201)
async def add_comment(
    article_id: uuid.UUID,
    body: AddCommentRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ArticleService, Depends(get_article_service)],
) -> CommentResponse:
    comment = await service.add_comment(article_id, current_user, body.text)
    return CommentResponse(**comment.model_dump())


@router.delete("/articles/comments/{comment_id}", response_model=dict)
async def delete_comment(
    comment_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ArticleService, Depends(get_article_service)],
) -> dict:
    await service.delete_comment(comment_id, current_user)
    return {"message": "Удалено"}
