import contextlib
from datetime import datetime
from typing import AsyncIterator, Optional

from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy_utc import UtcDateTime, utcnow

Base = declarative_base()


class SubBaseEntity(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        UtcDateTime(timezone=True), nullable=False, server_default=utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        UtcDateTime(timezone=True),
        nullable=False,
        server_default=utcnow(),
        onupdate=utcnow(),
    )


class BaseEntity(SubBaseEntity):
    __abstract__ = True
    uuid: Mapped[Optional[str]] = mapped_column(String, unique=True)


class DatabaseSessionManager:
    def __init__(self):
        self._init_done = False
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker | None = None

    def init(self, host: str, comment: str = None):
        self._comment = comment
        self._engine = create_async_engine(host)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)
        self._init_done = True

    def init_done(self):
        return self._init_done

    async def close(self):
        if self._engine is None:
            raise RuntimeError("DatabaseSessionManager is not initialized")

        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise RuntimeError("Connect: DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise RuntimeError("Session: DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    # Used for testing

    async def create_all(self, connection: AsyncConnection):
        await connection.run_sync(Base.metadata.create_all)

    async def drop_all(self, connection: AsyncConnection):
        await connection.run_sync(Base.metadata.drop_all)


sessionmanager = DatabaseSessionManager()


async def get_db():
    async with sessionmanager.session() as session:
        yield session
