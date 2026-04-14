import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ArticleListItemResponse(BaseModel):
    id: uuid.UUID
    title: str
    preview: str
    tags: list[str]
    status: str
    created_at: datetime
    likes_count: int
    comments_count: int
    is_new: bool


class ArticleDetailResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    preview: str
    tags: list[str]
    status: str
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    likes_count: int
    comments_count: int
    user_liked: bool


class CreateDraftResponse(BaseModel):
    id: str
    status: str


class UpdateArticleRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None
    status: str | None = None


class LikeResponse(BaseModel):
    liked: bool
    likes_count: int


class CommentResponse(BaseModel):
    id: uuid.UUID
    article_id: uuid.UUID
    user_id: uuid.UUID
    display_name: str
    email: str | None = None
    text: str
    created_at: datetime


class AddCommentRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class ImageUploadResponse(BaseModel):
    id: str
    url: str
