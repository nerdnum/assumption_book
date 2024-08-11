from sqlalchemy import String, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from slugify import slugify
from typing import Union


from app.services.database import BaseEntity


class Project(BaseEntity):
    __tablename__ = "projects"
    title: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=True)
    description: Mapped[str] = mapped_column(
        String(255), nullable=True)
    project_manager: Mapped[str] = mapped_column(
        String(100), nullable=True)
    logo_url: Mapped[str] = mapped_column(String(255), nullable=True)

    @classmethod
    async def get_all(cls, db: AsyncSession) -> list["Project"]:
        projects = (await db.execute(select(cls))).scalars().all()
        return projects

    @classmethod
    async def create(cls, db: AsyncSession, title: str, description: str | None, slug: str | None,
                     project_manager: str | None, logo_url: str | None) -> "Project":

        if slug is None:
            slug = slugify(title)

        project = cls(title=title, description=description,
                      project_manager=project_manager, slug=slug, uuid=str(uuid4()))

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
                raise NoResultFound
        except NoResultFound:
            raise ValueError("Project not found")
        return project

    @classmethod
    async def get_by_slug(cls, db: AsyncSession, slug: str) -> "Project":
        try:
            project = (await db.execute(select(cls).where(cls.slug == slug))).scalar_one()
            if project is None:
                raise NoResultFound
        except NoResultFound:
            raise ValueError("Project not found")
        return project

    @classmethod
    async def get_id_by_slug(cls, db: AsyncSession, slug: str) -> "Project":
        try:
            project = (await db.execute(select(cls).where(cls.slug == slug))).scalar_one()
            if project is None:
                raise NoResultFound
        except NoResultFound:
            raise ValueError("Project not found")
        return project.id

    @classmethod
    async def update_project(cls, db: AsyncSession, id: int, title: str | None, description: str | None, slug: str | None, project_manager: str | None, logo_url: str | None) -> "Project":
        try:
            project = await db.get(cls, id)
            if title is not None:
                project.title = title
            if description is not None:
                project.description = description
            if slug is not None:
                print('Got slug', slug)
                if slug == slugify(slug):
                    print('Slug is valid')
                    project.slug = slug
            else:
                project.slug = slugify(project.title)
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
    async def update_by_id(cls, db: AsyncSession, id: int, title: str | None, description: str | None, slug: str | None, project_manager: str | None, logo_url: str | None) -> "Project":
        return await cls.update_project(db, id, title, description, slug, project_manager, logo_url)

    @classmethod
    async def update_by_slug(cls, db: AsyncSession, lookup_slug: str, title: str | None, slug: str | None, description: str | None, project_manager: str | None, logo_url: str | None) -> "Project":
        try:
            project_id = await cls.get_id_by_slug(db, lookup_slug)
            project = await cls.update_project(
                db, project_id, title, description, slug, project_manager, logo_url)
        except NoResultFound:
            raise ValueError("Project not found")
        return project

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

    @classmethod
    async def delete_by_slug(cls, db: AsyncSession, slug: str) -> None:
        try:
            project = await cls.get_by_slug(db, slug)
            if project is None:
                raise NoResultFound
            await db.delete(project)
            await db.commit()
        except NoResultFound:
            raise ValueError("Project not found")
        return project
