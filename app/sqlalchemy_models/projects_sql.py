from uuid import uuid4

from sqlalchemy import String, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.services.database import BaseEntity


class Project(BaseEntity):
    __tablename__ = "projects"
    title: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    project_manager: Mapped[str] = mapped_column(String(100), nullable=True)
    logo_url: Mapped[str] = mapped_column(String(255), nullable=True)

    @classmethod
    async def get_all(cls, db: AsyncSession) -> list["Project"]:
        projects = (await db.execute(select(cls))).scalars().all()
        return projects

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        title: str,
        description: str | None,
        project_manager: str | None,
        logo_url: str | None,
    ) -> "Project":

        project = cls(
            title=title,
            description=description,
            project_manager=project_manager,
            uuid=str(uuid4()),
        )

        try:
            db.add(project)
            await db.commit()
            await db.refresh(project)
        except IntegrityError:
            await db.rollback()
            raise ValueError("Project with this title already exists")
        return project

    @classmethod
    async def get_by_id(cls, db: AsyncSession, id: int) -> "Project":
        try:
            project = await db.get(cls, id)
            if project is None:
                raise ValueError("Project not found")
        except Exception as error:
            raise error

        return project

    @classmethod
    async def update_project(
        cls,
        db: AsyncSession,
        id: int,
        title: str | None,
        description: str | None,
        project_manager: str | None,
        logo_url: str | None,
    ) -> "Project":
        try:
            project = await db.get(cls, id)
            if title is not None:
                project.title = title
            if description is not None:
                project.description = description
            if logo_url is not None:
                project.logo_url = logo_url
            if project_manager is not None:
                project.project_manager = project_manager
            try:
                await db.commit()
                await db.refresh(project)
            except IntegrityError:
                await db.rollback()
                raise ValueError("Project with this title already exists")
        except NoResultFound:
            raise ValueError("Project not found")
        return project

    @classmethod
    async def update_by_id(
        cls,
        db: AsyncSession,
        id: int,
        title: str | None,
        description: str | None,
        project_manager: str | None,
        logo_url: str | None,
    ) -> "Project":
        return await cls.update_project(
            db, id, title, description, project_manager, logo_url
        )

    @classmethod
    async def delete_by_id(cls, db: AsyncSession, id: int) -> None:
        try:
            project = await db.get(cls, id)
            if project is None:
                raise NoResultFound
            await db.delete(project)
            await db.commit()
        except NoResultFound:
            raise ValueError("Project not found")
        return project
