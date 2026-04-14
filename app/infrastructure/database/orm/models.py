from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Boolean, Text, LargeBinary
from sqlalchemy.dialects.postgresql import UUID, ARRAY

import uuid
from typing import List

from app.infrastructure.database.base import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    subscribes: Mapped[List["Subscribes"]] = relationship(
        "Subscribes", back_populates="user", cascade="all, delete-orphan"
    )


class Subscribes(Base):
    __tablename__ = "subscribes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ip: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[str] = mapped_column(String(10), nullable=False)
    # payload хранится как шаблон с {ip} и {port} — подстановка при выдаче
    payload: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["Users"] = relationship("Users", back_populates="subscribes")


class ArticleStatus(str):
    DRAFT = "draft"
    PUBLISHED = "published"
    HIDDEN = "hidden"


class Articles(Base):
    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    preview: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tags: Mapped[list] = mapped_column(
        ARRAY(String(100)), nullable=False, server_default="{}"
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    images: Mapped[List["ArticleImages"]] = relationship(
        "ArticleImages", back_populates="article", cascade="all, delete-orphan"
    )
    likes: Mapped[List["ArticleLikes"]] = relationship(
        "ArticleLikes", back_populates="article", cascade="all, delete-orphan"
    )
    comments: Mapped[List["ArticleComments"]] = relationship(
        "ArticleComments", back_populates="article", cascade="all, delete-orphan"
    )


class ArticleImages(Base):
    __tablename__ = "article_images"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    article_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=True, index=True
    )
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    article: Mapped["Articles | None"] = relationship("Articles", back_populates="images")


class ArticleLikes(Base):
    __tablename__ = "article_likes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    article: Mapped["Articles"] = relationship("Articles", back_populates="likes")


class ArticleComments(Base):
    __tablename__ = "article_comments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)

    article: Mapped["Articles"] = relationship("Articles", back_populates="comments")
