import re
import uuid
from datetime import datetime, timezone, timedelta

from app.infrastructure.database.uow import UnitOfWorkWithArticles
from app.domain.models.models import User
from app.domain.models.articles import ArticleListItem, ArticleDetail, CommentOut
from app.domain.exceptions.base import AppException, ForbiddenError


def _strip_markdown(text: str) -> str:
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[.*?\]\(.*?\)', r'\1', text)
    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'[*_`~>]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _generate_preview(content: str) -> str:
    stripped = _strip_markdown(content)
    if len(stripped) <= 200:
        return stripped
    return stripped[:200].rstrip() + '...'


def _anon_display(user_id: uuid.UUID) -> str:
    num = int(str(user_id).replace('-', '')[:8], 16) % 9999
    return f"Аноним #{num:04d}"


class ArticleService:

    def __init__(self, uow: UnitOfWorkWithArticles) -> None:
        self.uow = uow

    # ── List ───────────────────────────────────────────────────────────────

    async def get_list(self, current_user: User,
                       search: str | None = None,
                       tag: str | None = None) -> list[ArticleListItem]:
        now = datetime.now(timezone.utc)

        if current_user.is_superuser:
            articles = await self.uow.articles.get_all_for_admin(search, tag)
        else:
            articles = await self.uow.articles.get_published(search, tag)

        result = []
        for a in articles:
            likes = await self.uow.articles.count_likes(a.id)
            comments = await self.uow.articles.count_comments(a.id)
            created = a.created_at if a.created_at.tzinfo else a.created_at.replace(tzinfo=timezone.utc)
            is_new = (now - created) < timedelta(days=3)
            result.append(ArticleListItem(
                id=a.id, title=a.title, preview=a.preview,
                tags=a.tags or [], status=a.status,
                created_at=a.created_at,
                likes_count=likes, comments_count=comments, is_new=is_new,
            ))
        return result

    # ── Detail ─────────────────────────────────────────────────────────────

    async def get_detail(self, article_id: uuid.UUID, current_user: User) -> ArticleDetail:
        article = await self.uow.articles.get_by_id(article_id)
        if not article:
            raise AppException("Статья не найдена")
        if article.status != "published" and not current_user.is_superuser:
            raise AppException("Статья не найдена")

        likes = await self.uow.articles.count_likes(article_id)
        comments = await self.uow.articles.count_comments(article_id)
        liked = await self.uow.articles.user_liked(article_id, current_user.id)

        return ArticleDetail(
            id=article.id, title=article.title, content=article.content,
            preview=article.preview, tags=article.tags or [],
            status=article.status, author_id=article.author_id,
            created_at=article.created_at, updated_at=article.updated_at,
            likes_count=likes, comments_count=comments, user_liked=liked,
        )

    # ── Create draft ───────────────────────────────────────────────────────

    async def create_draft(self, current_user: User) -> dict:
        if not current_user.is_superuser:
            raise ForbiddenError()
        article = await self.uow.articles.add_article(
            id=uuid.uuid4(),
            title="",
            content="",
            preview="",
            tags=[],
            status="draft",
            author_id=current_user.id,
        )
        return {"id": str(article.id), "status": "draft"}

    # ── Update ─────────────────────────────────────────────────────────────

    async def update(self, article_id: uuid.UUID, current_user: User,
                     title: str | None = None, content: str | None = None,
                     tags: list[str] | None = None, status: str | None = None) -> None:
        if not current_user.is_superuser:
            raise ForbiddenError()

        article = await self.uow.articles.get_by_id(article_id)
        if not article:
            raise AppException("Статья не найдена")

        updates: dict = {}
        if title is not None:
            updates["title"] = title
        if content is not None:
            updates["content"] = content
            updates["preview"] = _generate_preview(content)
        if tags is not None:
            updates["tags"] = tags
        if status is not None:
            allowed = {"draft", "published", "hidden"}
            if status not in allowed:
                raise AppException(f"Статус должен быть одним из: {allowed}")
            updates["status"] = status

        if updates:
            await self.uow.articles.update_article(article_id, **updates)

    # ── Delete ─────────────────────────────────────────────────────────────

    async def delete(self, article_id: uuid.UUID, current_user: User) -> None:
        if not current_user.is_superuser:
            raise ForbiddenError()
        article = await self.uow.articles.get_by_id(article_id)
        if not article:
            raise AppException("Статья не найдена")
        await self.uow.articles.delete_article(article_id)

    # ── Images ─────────────────────────────────────────────────────────────

    async def upload_image(self, article_id: uuid.UUID | None,
                           current_user: User,
                           data: bytes, mime_type: str, filename: str) -> dict:
        if not current_user.is_superuser:
            raise ForbiddenError()
        img = await self.uow.articles.save_image(article_id, data, mime_type, filename)
        return {"id": str(img.id), "url": f"/api/v1/images/{img.id}"}

    async def get_image(self, image_id: uuid.UUID) -> tuple[bytes, str]:
        img = await self.uow.articles.get_image(image_id)
        if not img:
            raise AppException("Изображение не найдено")
        return img.data, img.mime_type

    # ── Likes ──────────────────────────────────────────────────────────────

    async def toggle_like(self, article_id: uuid.UUID, current_user: User) -> dict:
        article = await self.uow.articles.get_by_id(article_id)
        if not article:
            raise AppException("Статья не найдена")
        liked = await self.uow.articles.toggle_like(article_id, current_user.id)
        count = await self.uow.articles.count_likes(article_id)
        return {"liked": liked, "likes_count": count}

    # ── Comments ───────────────────────────────────────────────────────────

    async def get_comments(self, article_id: uuid.UUID,
                           current_user: User) -> list[CommentOut]:
        article = await self.uow.articles.get_by_id(article_id)
        if not article:
            raise AppException("Статья не найдена")

        comments = await self.uow.articles.get_comments(article_id)
        result = []
        for c in comments:
            user_obj = await self.uow.articles.get_user_by_id(c.user_id)
            email = user_obj.email if (current_user.is_superuser and user_obj) else None
            result.append(CommentOut(
                id=c.id, article_id=c.article_id, user_id=c.user_id,
                display_name=_anon_display(c.user_id),
                email=email, text=c.text, created_at=c.created_at,
            ))
        return result

    async def add_comment(self, article_id: uuid.UUID,
                          current_user: User, text: str) -> CommentOut:
        article = await self.uow.articles.get_by_id(article_id)
        if not article or article.status != "published" and not current_user.is_superuser:
            raise AppException("Статья не найдена")

        comment = await self.uow.articles.add_comment(article_id, current_user.id, text)
        email = current_user.email if current_user.is_superuser else None
        return CommentOut(
            id=comment.id, article_id=comment.article_id, user_id=comment.user_id,
            display_name=_anon_display(comment.user_id),
            email=email, text=comment.text, created_at=comment.created_at,
        )

    async def delete_comment(self, comment_id: uuid.UUID, current_user: User) -> None:
        comment = await self.uow.articles.get_comment(comment_id)
        if not comment:
            raise AppException("Комментарий не найден")
        if not current_user.is_superuser and comment.user_id != current_user.id:
            raise ForbiddenError()
        await self.uow.articles.delete_comment(comment_id)
