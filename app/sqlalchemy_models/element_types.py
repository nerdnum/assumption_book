from fastapi import HTTPException
from sqlalchemy import select, String, CheckConstraint
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4

from app.services.database import BaseEntity


class ElementType(BaseEntity):
    __tablename__ = "element_types"

    title: Mapped[str] = mapped_column(
        String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    default_text: Mapped[str] = mapped_column(String, nullable=True)

    __table_args__ = (CheckConstraint(
        'length(title) > 0', name='title_length'), )

    @classmethod
    async def get_all(cls, db):
        return (await db.execute(select(cls))).scalars().all()

    @classmethod
    async def create(cls, db: AsyncSession, title: str, description: str | None, default_text: str | None) -> "ElementType":
        element_type = cls(title=title, description=description,
                           default_text=default_text, uuid=str(uuid4()))
        try:
            db.add(element_type)
            await db.commit()
            await db.refresh(element_type)
        except IntegrityError as error:
            await db.rollback()
            error_str = str(error)
            if error_str.find('new row for relation "element_types" violates check constraint "title_length"') != -1:
                raise HTTPException(
                    status_code=422, detail="Title field cannot be empty")
            raise ValueError("Element type with this title already exists")
        except Exception as error:
            await db.rollback()
            raise
        return element_type

    @classmethod
    async def get(cls, db: AsyncSession, id: int) -> "ElementType":
        try:
            element_type = await db.get(cls, id)
            if element_type is None:
                raise NoResultFound
        except NoResultFound:
            raise ValueError("Element type not found")
        except Exception:
            raise
        return element_type

    @classmethod
    async def update(cls, db: AsyncSession, id: int, title: str, description: str | None, default_text: str | None) -> "ElementType":
        try:
            element_type = await db.get(cls, id)
            if element_type is None:
                raise NoResultFound
            if title is not None:
                element_type.title = title
            if description is not None:
                element_type.description = description
            if default_text is not None:
                element_type.default_text = default_text
            await db.commit()
            await db.refresh(element_type)
        except NoResultFound:
            raise ValueError("Element type not found")
        except IntegrityError as error:
            await db.rollback()
            error_str = str(error)
            if error_str.find('new row for relation "element_types" violates check constraint "title_length"') != -1:
                raise ValueError("Title field cannot be empty")
            raise ValueError("Element type with this title already exists")
        except Exception:
            await db.rollback()
            raise
        return element_type

    @classmethod
    async def delete(cls, db: AsyncSession, id: int) -> None:
        try:
            element_type = await db.get(cls, id)
            if element_type is None:
                raise NoResultFound
            await db.delete(element_type)
            await db.commit()
        except NoResultFound:
            print('No result found')
            raise ValueError("Element type not found")
        except Exception:
            await db.rollback()
            raise
        return {'detail': "Element type deleted"}
