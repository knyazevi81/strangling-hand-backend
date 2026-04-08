from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from typing import TypeVar, Generic, Type

from app.domain.repositories.base import Repository

Model = TypeVar("Model")


class ModelBaseRepository(Repository[Model], Generic[Model]):

    def __init__(self, session: AsyncSession, model: Type[Model]):
        self.session = session
        self.model = model

    async def get_by_id(self, model_id):
        result = await self.session.execute(
            select(self.model).filter_by(id=model_id)
        )
        return result.scalar_one_or_none()

    async def find_one_or_none(self, **filter_by):
        result = await self.session.execute(
            select(self.model).filter_by(**filter_by)
        )
        return result.scalars().first()

    async def find_all(self, **filter_by):
        result = await self.session.execute(
            select(self.model).filter_by(**filter_by)
        )
        return result.scalars().all()

    async def add(self, **data):
        await self.session.execute(
            insert(self.model).values(**data)
        )
