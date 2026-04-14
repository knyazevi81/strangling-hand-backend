from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, func
import uuid
from typing import List

from app.infrastructure.database.orm.models import Articles, ArticleImages, ArticleLikes, ArticleComments
from app.infrastructure.database.repositories.base import ModelBaseRepository


class SQLArticleRepository(ModelBaseRepository[Articles]):

    def __init__(self, session: AsyncSession):
        super().__init__(session, Articles)

    async def get_by_id(self, article_id: uuid.UUID) -> Articles | None:
        result = await self.session.execute(
            select(Articles).filter_by(id=article_id)
        )
        return result.scalar_one_or_none()

    async def get_published(self, search: str | None = None, tag: str | None = None) -> List[Articles]:
        stmt = select(Articles).where(Articles.status == "published")
        if search:
            stmt = stmt.where(
                Articles.title.ilike(f"%{search}%") | Articles.preview.ilike(f"%{search}%")
            )
        if tag:
            stmt = stmt.where(Articles.tags.contains([tag]))
        stmt = stmt.order_by(Articles.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_for_admin(self, search: str | None = None, tag: str | None = None) -> List[Articles]:
        stmt = select(Articles).where(Articles.status != "deleted")
        if search:
            stmt = stmt.where(
                Articles.title.ilike(f"%{search}%") | Articles.preview.ilike(f"%{search}%")
            )
        if tag:
            stmt = stmt.where(Articles.tags.contains([tag]))
        stmt = stmt.order_by(Articles.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_article(self, **data) -> Articles:
        result = await self.session.execute(
            insert(Articles).values(**data).returning(Articles)
        )
        await self.session.flush()
        return result.scalar_one()

    async def update_article(self, article_id: uuid.UUID, **data) -> None:
        await self.session.execute(
            update(Articles).where(Articles.id == article_id).values(**data)
        )

    async def delete_article(self, article_id: uuid.UUID) -> None:
        await self.session.execute(
            delete(Articles).where(Articles.id == article_id)
        )

    async def count_likes(self, article_id: uuid.UUID) -> int:
        result = await self.session.execute(
            select(func.count()).where(ArticleLikes.article_id == article_id)
        )
        return result.scalar() or 0

    async def count_comments(self, article_id: uuid.UUID) -> int:
        result = await self.session.execute(
            select(func.count()).where(ArticleComments.article_id == article_id)
        )
        return result.scalar() or 0

    async def user_liked(self, article_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        result = await self.session.execute(
            select(ArticleLikes).where(
                ArticleLikes.article_id == article_id,
                ArticleLikes.user_id == user_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def toggle_like(self, article_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        existing = await self.session.execute(
            select(ArticleLikes).where(
                ArticleLikes.article_id == article_id,
                ArticleLikes.user_id == user_id,
            )
        )
        obj = existing.scalar_one_or_none()
        if obj:
            await self.session.execute(
                delete(ArticleLikes).where(
                    ArticleLikes.article_id == article_id,
                    ArticleLikes.user_id == user_id,
                )
            )
            return False
        else:
            await self.session.execute(
                insert(ArticleLikes).values(
                    id=uuid.uuid4(), article_id=article_id, user_id=user_id
                )
            )
            return True

    async def get_comments(self, article_id: uuid.UUID) -> List[ArticleComments]:
        result = await self.session.execute(
            select(ArticleComments)
            .where(ArticleComments.article_id == article_id)
            .order_by(ArticleComments.created_at.asc())
        )
        return list(result.scalars().all())

    async def add_comment(self, article_id: uuid.UUID, user_id: uuid.UUID, text: str) -> ArticleComments:
        comment_id = uuid.uuid4()
        await self.session.execute(
            insert(ArticleComments).values(
                id=comment_id, article_id=article_id, user_id=user_id, text=text
            )
        )
        await self.session.flush()
        result = await self.session.execute(
            select(ArticleComments).where(ArticleComments.id == comment_id)
        )
        return result.scalar_one()

    async def get_comment(self, comment_id: uuid.UUID) -> ArticleComments | None:
        result = await self.session.execute(
            select(ArticleComments).where(ArticleComments.id == comment_id)
        )
        return result.scalar_one_or_none()

    async def delete_comment(self, comment_id: uuid.UUID) -> None:
        await self.session.execute(
            delete(ArticleComments).where(ArticleComments.id == comment_id)
        )

    async def save_image(self, article_id: uuid.UUID | None, data: bytes, mime_type: str, filename: str) -> ArticleImages:
        img_id = uuid.uuid4()
        await self.session.execute(
            insert(ArticleImages).values(
                id=img_id, article_id=article_id,
                data=data, mime_type=mime_type, filename=filename,
            )
        )
        await self.session.flush()
        result = await self.session.execute(
            select(ArticleImages).where(ArticleImages.id == img_id)
        )
        return result.scalar_one()

    async def get_image(self, image_id: uuid.UUID) -> ArticleImages | None:
        result = await self.session.execute(
            select(ArticleImages).where(ArticleImages.id == image_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: uuid.UUID):
        from app.infrastructure.database.orm.models import Users
        result = await self.session.execute(
            select(Users).where(Users.id == user_id)
        )
        return result.scalar_one_or_none()
