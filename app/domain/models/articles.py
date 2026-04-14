import uuid
from datetime import datetime
from pydantic import BaseModel


class ArticleListItem(BaseModel):
    id: uuid.UUID
    title: str
    preview: str
    tags: list[str]
    status: str
    created_at: datetime
    likes_count: int
    comments_count: int
    is_new: bool

    model_config = {"from_attributes": True}


class ArticleDetail(BaseModel):
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

    model_config = {"from_attributes": True}


class CommentOut(BaseModel):
    id: uuid.UUID
    article_id: uuid.UUID
    user_id: uuid.UUID
    display_name: str
    email: str | None
    text: str
    created_at: datetime

    model_config = {"from_attributes": True}
