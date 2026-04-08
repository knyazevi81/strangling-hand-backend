from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.repositories.vpn import (
    SQLUserRepository,
    SQLSubscribeRepository,
)
from app.domain.repositories.uow import AbstractUnitOfWork
from app.infrastructure.database.engine import async_session_maker


class UnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __aenter__(self):
        self.users = SQLUserRepository(self.session)
        self.subscribes = SQLSubscribeRepository(self.session)
        return self

    async def __aexit__(self, exc_type, *args):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()


class UnitOfWorkFactory:
    async def __aenter__(self):
        self._session = async_session_maker()
        session = await self._session.__aenter__()
        self._uow = UnitOfWork(session)
        return await self._uow.__aenter__()

    async def __aexit__(self, *args):
        await self._uow.__aexit__(*args)
        await self._session.__aexit__(*args)
