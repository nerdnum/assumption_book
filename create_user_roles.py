import contextlib
import uuid

from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from datetime import datetime
from typing import Optional, AsyncIterator

from app.sqlalchemy_models.user_project_role_sql import (
    Role as SqlRole,
    Project as SqlProject,
    ProjectRole as SqlProjectRole,
)
import asyncio


db_url = "postgresql+asyncpg://postgres:Xupo1074!@192.168.52.193/assumptions"

eng = create_async_engine(db_url)

role_list = [
    [
        "project_creator",
        "User can edit and change projects and their base information.",
        True,
        True,
    ],
    [
        "project_viewer",
        "User can explore a project but not change anything",
        True,
        False,
    ],
    ["component_editor", "User can edit project components", True, False],
    ["document_editor", "User can edit project documents", True, False],
    ["excel_exporter", "Can export Excel documents", True, False],
    ["word_exporter", "Can export Word documents", True, False],
]


@contextlib.asynccontextmanager
async def connect() -> AsyncIterator[AsyncConnection]:
    async with eng.connect() as conn:
        yield conn
    await conn.close()


@contextlib.asynccontextmanager
async def session_maker() -> AsyncIterator[AsyncSession]:
    async with connect() as con:
        session = async_sessionmaker(con, autocommit=False, expire_on_commit=False)()
        yield session
    await session.close()


async def check_roles():
    async with session_maker() as session:
        roles = (await session.execute(select(SqlRole))).scalars().all()
        print(roles)


async def create_user_roles():
    async with session_maker() as session:
        for role in role_list:
            new_role = SqlRole(
                name=role[0],
                description=role[1],
                is_active=role[2],
                is_system_role=role[3],
                uuid=None,  # UUID will be generated automatically
                created_by=1,  # Assuming a default user ID for creation
                updated_by=1,  # Assuming a default user ID for update
            )
            session.add(new_role)
        session.commit()


async def create_roles_for_projects():
    async with session_maker() as session:
        roles = (
            (
                await session.execute(
                    select(SqlRole)
                    .where(SqlRole.is_system_role == False)
                    .order_by(SqlRole.id)
                )
            )
            .scalars()
            .all()
        )
        for role in roles:
            print(
                f"Role: {role.name}, Description: {role.description}, Active: {role.is_active}"
            )
        # Here you can add logic to assign these roles to specific projects or users if needed
        projects = (await session.execute(select(SqlProject))).scalars().all()
        for project in projects:
            for role in roles:
                new_project_role = SqlProjectRole(
                    project_id=project.id,
                    role_id=role.id,
                    uuid=str(uuid.uuid4()),  # Generate a new UUID
                    created_by=1,  # Assuming a default user ID for creation
                    updated_by=1,  # Assuming a default user ID for update
                )
                session.add(new_project_role)
        await session.commit()


if __name__ == "__main__":
    # asyncio.run(create_user_roles())
    asyncio.run(create_roles_for_projects())
