import contextlib
from sqlalchemy import select, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship, selectinload
from sqlalchemy.ext.asyncio import (
    AsyncConnection, AsyncEngine, AsyncSession,
    async_sessionmaker, create_async_engine
)
from datetime import datetime
from typing import Optional, AsyncIterator
from sqlalchemy_utc import UtcDateTime, utcnow
from app.pydantic_models.component_model import ComponentWithDescendants, Component as PydanticComponent
import asyncio

Base = declarative_base()


class Component(Base):
    __tablename__ = "components"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime(timezone=True),
                                                 nullable=False, server_default=utcnow())
    updated_at: Mapped[datetime] = mapped_column(UtcDateTime(timezone=True), nullable=False,
                                                 server_default=utcnow(), onupdate=utcnow())
    uuid: Mapped[Optional[str]] = mapped_column(String, unique=True)
    parent_id = mapped_column(Integer, ForeignKey("components.id"))
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String, nullable=False)
    uuid: Mapped[str] = mapped_column(String, nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String)
    descendants: Mapped[list["Component"]] = relationship(
        "Component")

    def __str__(self):
        return f"{self.id}: {self.title}"
        # return f"{self.title}, {[ch.title for ch in self.descendants]}"


db_url = "postgresql+asyncpg://postgres:!Nerdnum#1@localhost/fastapi"

eng = create_async_engine(db_url)


@contextlib.asynccontextmanager
async def connect() -> AsyncIterator[AsyncConnection]:
    async with eng.connect() as conn:
        yield conn
    await conn.close()


@contextlib.asynccontextmanager
async def session_maker() -> AsyncIterator[AsyncSession]:
    async with connect() as con:
        session = async_sessionmaker(con, autocommit=False)()
        yield session
    await session.close()


async def get_component():
    async with session_maker() as session:
        # .options(selectinload(Component.descendants))
        comp = (await session.execute(select(Component).where(Component.id == 60).options(selectinload(Component.descendants)))).scalars().first()
        print(comp)
        for descendant in comp.descendants:
            print(descendant)
            if len(descendant.descendants) > 0:
                for d in descendant.descendants:
                    print(d)


if __name__ == "__main__":
    asyncio.run(get_component())
