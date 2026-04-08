from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

import uuid
from typing import List

from app.domain.models.models import User, Subscribe
from app.infrastructure.database.orm.models import Users, Subscribes
from app.infrastructure.database.repositories.base import ModelBaseRepository


class SQLUserRepository(ModelBaseRepository[Users]):

    def __init__(self, session: AsyncSession):
        super().__init__(session, Users)

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(
            select(Users).filter_by(id=user_id)
        )
        obj = result.scalar_one_or_none()
        return User.model_validate(obj) if obj else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(Users).filter_by(email=email)
        )
        obj = result.scalar_one_or_none()
        return User.model_validate(obj) if obj else None

    async def find_one_or_none(self, **filter_by) -> User | None:
        result = await self.session.execute(
            select(Users).filter_by(**filter_by)
        )
        obj = result.scalars().first()
        return User.model_validate(obj) if obj else None

    async def find_all(self, **filter_by) -> List[User]:
        result = await self.session.execute(
            select(Users).filter_by(**filter_by)
        )
        return [User.model_validate(obj) for obj in result.scalars().all()]

    async def add(self, **data) -> None:
        await self.session.execute(
            insert(Users).values(**data)
        )

    async def activate(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            update(Users).where(Users.id == user_id).values(is_active=True)
        )

    async def change_password(self, user_id: uuid.UUID, hashed_password: str) -> None:
        await self.session.execute(
            update(Users).where(Users.id == user_id).values(hashed_password=hashed_password)
        )


class SQLSubscribeRepository(ModelBaseRepository[Subscribes]):

    def __init__(self, session: AsyncSession):
        super().__init__(session, Subscribes)

    async def get_by_id(self, subscribe_id: uuid.UUID) -> Subscribe | None:
        result = await self.session.execute(
            select(Subscribes).filter_by(id=subscribe_id)
        )
        obj = result.scalar_one_or_none()
        return Subscribe.model_validate(obj) if obj else None

    async def find_one_or_none(self, **filter_by) -> Subscribe | None:
        result = await self.session.execute(
            select(Subscribes).filter_by(**filter_by)
        )
        obj = result.scalars().first()
        return Subscribe.model_validate(obj) if obj else None

    async def find_all(self, **filter_by) -> List[Subscribe]:
        result = await self.session.execute(
            select(Subscribes).filter_by(**filter_by)
        )
        return [Subscribe.model_validate(obj) for obj in result.scalars().all()]

    async def find_by_user_id(self, user_id: uuid.UUID) -> List[Subscribe]:
        result = await self.session.execute(
            select(Subscribes).where(Subscribes.user_id == user_id)
        )
        return [Subscribe.model_validate(obj) for obj in result.scalars().all()]

    async def add(self, **data) -> None:
        await self.session.execute(
            insert(Subscribes).values(**data)
        )

    async def update(self, subscribe_id: uuid.UUID, **data) -> None:
        await self.session.execute(
            update(Subscribes).where(Subscribes.id == subscribe_id).values(**data)
        )

    async def delete(self, subscribe_id: uuid.UUID) -> None:
        await self.session.execute(
            delete(Subscribes).where(Subscribes.id == subscribe_id)
        )

    async def get_hashed_password(self, email: str) -> str | None:
        from sqlalchemy import select
        from app.infrastructure.database.orm.models import Users
        result = await self.session.execute(
            select(Users.hashed_password).filter_by(email=email)
        )
        return result.scalar_one_or_none()
