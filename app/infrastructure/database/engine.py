from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from app.infrastructure.config.config import get_settings

setting = get_settings()

engine = create_async_engine(
    setting.database_url
)

async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
