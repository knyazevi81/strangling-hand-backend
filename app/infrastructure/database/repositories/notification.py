from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

import uuid
from typing import List

from app.domain.models.notification import Template, Channel, Client, NotificationSent
from app.domain.repositories.notification import (
    TemplateRepository,
    ClientRepository,
    ChannelRepository,
    NotificationSentRepository
)
from app.infrastructure.database.orm.models import (
    NotificationTemplate,
    NotificationClient,
    NotificationChannel,
    NotificationSent as OrmModelNotificationSent
)


class SQLTemplateRepository(TemplateRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: uuid.UUID) -> Template | None:
        result = await self.session.execute(
            select(NotificationTemplate).filter_by(id=id)
        )
        obj = result.scalar_one_or_none()
        return Template.model_validate(obj) if obj else None

    async def find_one_or_none(self, **filters) -> Template | None:
        result = await self.session.execute(
            select(NotificationTemplate).filter(**filters)
        )
        obj = result.scalar().first()
        return Template.model_validate(obj) if obj else None

    async def find_all(self, **filters) -> List[Template] | None:
        result = await self.session.execute(
            select(NotificationTemplate).filter_by(**filters)
        )
        return [Template.model_validate(obj) for obj in result.scalars().all()]

    async def add(self, **data) -> None:
        await self.session.execute(insert(NotificationTemplate).values(**data))

    async def delete(self, id: uuid.UUID) -> None:
        await self.session.execute(
            delete(NotificationTemplate).filter_by(id=id)
        )
        
        
class SQLClientRepository(ClientRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: uuid.UUID) -> Client | None:
        result = await self.session.execute(
            select(NotificationClient).filter_by(id=id)
        )
        obj = result.scalar_one_or_none()
        return Client.model_validate(obj) if obj else None

    async def find_one_or_none(self, **filters) -> Client | None:
        result = await self.session.execute(
            select(NotificationClient).filter_by(**filters)
        )
        obj = result.scalar()
        return Client.model_validate(obj) if obj else None

    async def find_all(self, **filters) -> List[Client] | None:
        result = await self.session.execute(
            select(NotificationClient).filter_by(**filters)
        )
        return [Client.model_validate(obj) for obj in result.scalars().all()]

    async def add(self, **data) -> None:
        await self.session.execute(insert(NotificationClient).values(**data))

    async def get_many(self, ids: List[uuid.UUID]) -> List[Client] | None:
        result = await self.session.execute(
            select(NotificationClient).where(NotificationClient.id.in_(ids))
        )
        return [Client.model_validate(obj) for obj in result.scalars().all()]
    
        
class SQLChannelRepository(ChannelRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: uuid.UUID) -> Client | None:
        result = await self.session.execute(
            select(NotificationChannel).filter_by(id=id)
        )
        obj = result.scalar_one_or_none()
        return Channel.model_validate(obj) if obj else None

    async def find_one_or_none(self, **filters) -> Client | None:
        result = await self.session.execute(
            select(NotificationChannel).filter_by(**filters)
        )
        obj = result.scalar()
        return Channel.model_validate(obj) if obj else None

    async def find_all(self, **filters) -> List[Client] | None:
        result = await self.session.execute(
            select(NotificationChannel).filter_by(**filters)
        )
        return [Channel.model_validate(obj) for obj in result.scalars().all()]

    async def add(self, **data) -> None:
        await self.session.execute(insert(NotificationChannel).values(**data))
        
        
class SQLNotificationSentRepository(NotificationSentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: uuid.UUID) -> NotificationSent | None:
        result = await self.session.execute(
            select(OrmModelNotificationSent).filter_by(id=id)
        )
        obj = result.scalar_one_or_none()
        return NotificationSent.model_validate(obj) if obj else None

    async def find_one_or_none(self, **filters) -> NotificationSent | None:
        result = await self.session.execute(
            select(OrmModelNotificationSent).filter(**filters)
        )
        obj = result.scalar().first()
        return NotificationSent.model_validate(obj) if obj else None

    async def find_all(self, **filters) -> List[NotificationSent] | None:
        result = await self.session.execute(
            select(OrmModelNotificationSent).filter_by(**filters)
        )
        return [NotificationSent.model_validate(obj) for obj in result.scalars().all()]

    async def add(self, **data) -> None:
        await self.session.execute(insert(OrmModelNotificationSent).values(**data))