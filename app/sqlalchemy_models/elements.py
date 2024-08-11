from sqlalchemy import select, String, Integer, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4

from app.services.database import BaseEntity
from app.sqlalchemy_models.projects_sql import Project
from app.sqlalchemy_models.element_types import ElementType


class Element(BaseEntity):
    __tablename__ = "elements"

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False)
    element_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("element_types.id"), nullable=False)

    __table_args__ = (UniqueConstraint("project_id", "title"),
                      CheckConstraint('length(title) > 0', name='title_length'))

    @classmethod
    async def get_all(cls, db):
        return (await db.execute(select(cls))).scalars().all()

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     title: str,
                     description: str | None,
                     project_id: int,
                     element_type_id: int) -> "Element":

        element = cls(title=title,
                      description=description,
                      project_id=project_id,
                      element_type_id=element_type_id,
                      uuid=str(uuid4()))

        project = await Project.get(db, project_id)
        if project is None:
            raise ValueError("Project not found")

        element_type = await ElementType.get(db, element_type_id)
        if element_type is None:
            raise ValueError("Element type not found")

        possible_duplicate_error = \
            "Element '{}' already exists in project '{}'".format(
                title, project.title)

        try:
            db.add(element)
            await db.commit()
            await db.refresh(element)
        except IntegrityError as error:
            await db.rollback()
            error_str = str(error)
            if error_str.find('duplicate key value violates unique constraint "elements_project_id_title_key"') != -1:
                raise ValueError(possible_duplicate_error)
            if error_str.find('new row for relation "elements" violates check constraint "title_length"') != -1:
                raise ValueError("Title field cannot be empty")
            raise
        except Exception:
            await db.rollback()
            raise
        return element

    @classmethod
    async def get(cls, db: AsyncSession, id: int) -> "Element":
        try:
            element = await db.get(cls, id)
            if element is None:
                raise NoResultFound
        except NoResultFound:
            raise ValueError("Element not found")
        except Exception:
            raise
        return element

    @classmethod
    async def update(cls, db: AsyncSession, id: int, title: str | None, description: str | None, project_id: int | None, element_type_id: int | None) -> "Element":
        try:

            target_project_title = None
            target_element_title = None

            element = await db.get(cls, id)
            if element is None:
                raise NoResultFound

            if title is not None:
                element.title = title
                target_element_title = title
            else:
                target_element_title = element.title

            if description is not None:
                element.description = description

            if project_id is not None and project_id != element.project_id:
                project = await Project.get(db, project_id)
                if project is None:
                    raise ValueError("Project not found")
                target_project_title = project.title
                element.project_id = project_id

            if element_type_id is not None:
                element_type = await ElementType.get(db, element_type_id)
                if element_type is None:
                    raise ValueError("Element type not found")
                element.element_type_id = element_type_id

            possible_duplicate_error = f"Element '{
                target_element_title}' already exists in project '{target_project_title}'"

            try:
                await db.commit()
                await db.refresh(element)
            except IntegrityError as error:
                await db.rollback()
                error_str = str(error)
                if error_str.find('new row for relation "elements" violates check constraint "title_length"') != -1:
                    raise ValueError("Title field cannot be empty")
                raise ValueError(possible_duplicate_error)
        except NoResultFound:
            raise ValueError("Element not found")
        except Exception:
            raise
        return element

    @classmethod
    async def delete(cls, db: AsyncSession, id: int) -> None:
        try:
            element = await db.get(cls, id)
            if element is None:
                raise NoResultFound
            await db.delete(element)
            await db.commit()
        except NoResultFound:
            raise ValueError("Element not found")
        except Exception:
            raise
        return {'detail': "Element deleted"}
