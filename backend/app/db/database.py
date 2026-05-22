import asyncio
import logging
from collections.abc import AsyncGenerator

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = logging.getLogger(__name__)

_connect_args: dict = {}
_engine_kwargs: dict = {
    "echo": False,
    "pool_recycle": 1800,
    "pool_timeout": 30,
}

if settings.database_url.startswith("sqlite"):
    _connect_args = {"timeout": 30}
    _engine_kwargs["connect_args"] = _connect_args
    _engine_kwargs["pool_pre_ping"] = True
elif settings.database_url.startswith("mysql"):
    # pool_pre_ping breaks with aiomysql (ping() requires reconnect arg) — use pool_recycle instead
    _connect_args = {"connect_timeout": 10}
    _engine_kwargs["connect_args"] = _connect_args
    _engine_kwargs["pool_size"] = 5
    _engine_kwargs["max_overflow"] = 10
    _engine_kwargs["pool_pre_ping"] = False

engine = create_async_engine(settings.database_url, **_engine_kwargs)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@event.listens_for(engine.sync_engine, "connect")
def _sqlite_pragmas(dbapi_connection, _connection_record) -> None:
    if settings.database_url.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()


class Base(DeclarativeBase):
    pass


async def check_db_connection() -> bool:
    """Ping DB with retries — avoids flaky 'degraded' when pool is briefly busy."""
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            last_error = e
            if attempt < 2:
                await asyncio.sleep(0.15 * (attempt + 1))
    if last_error:
        logger.warning("database health check failed: %s", last_error)
    return False


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
