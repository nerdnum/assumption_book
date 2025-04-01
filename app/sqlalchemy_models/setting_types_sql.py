from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import CheckConstraint, String, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.services.database import BaseEntity


class SettingType(BaseEntity):
    __tablename__ = "setting_types"

    title: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    default_text: Mapped[str] = mapped_column(String, nullable=True)

    __table_args__ = (CheckConstraint("length(title) > 0", name="title_length"),)

    def __repr__(cls):
        return f"id:{cls.id}, title: {cls.title}"

    @classmethod
    async def get_all(cls, db):
        return (await db.execute(select(cls))).scalars().all()

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        title: str,
        description: str | None,
        default_text: str | None,
        user_id: int,
    ) -> "SettingType":
        setting_type = cls(
            title=title,
            description=description,
            default_text=default_text,
            uuid=str(uuid4()),
            created_by=user_id,
            updated_by=user_id,
        )
        try:
            db.add(setting_type)
            await db.commit()
            await db.refresh(setting_type)
        except IntegrityError as error:
            print("Found Integrity Error")
            print(error)
            await db.rollback()
            error_str = str(error)
            if (
                error_str.find(
                    'new row for relation "setting_types" violates check constraint "title_length"'
                )
                != -1
            ):
                raise HTTPException(
                    status_code=422, detail="Title field cannot be empty"
                )
            raise ValueError("Setting type with this title already exists")
        except Exception as error:
            await db.rollback()
            raise error
        return setting_type

    @classmethod
    async def get(cls, db: AsyncSession, id: int) -> "SettingType":
        try:
            setting_type = await db.get(cls, id)
            if setting_type is None:
                raise NoResultFound
        except NoResultFound:
            raise ValueError("Setting type not found")
        except Exception:
            raise
        return setting_type

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        id: int,
        title: str,
        description: str | None,
        default_text: str | None,
    ) -> "SettingType":
        try:
            setting_type = await db.get(cls, id)
            if setting_type is None:
                raise NoResultFound
            if title is not None:
                setting_type.title = title
            if description is not None:
                setting_type.description = description
            if default_text is not None:
                setting_type.default_text = default_text
            print(setting_type)
            await db.commit()
            await db.refresh(setting_type)
        except Exception as error:
            print(error)
            raise error
        # except NoResultFound:
        #     raise ValueError("Setting type not found")
        # except IntegrityError as error:
        #     await db.rollback()
        #     error_str = str(error)
        #     if (
        #         error_str.find(
        #             'new row for relation "setting_types" violates check constraint "title_length"'
        #         )
        #         != -1
        #     ):
        #         raise ValueError("Title field cannot be empty")
        #     raise ValueError("Setting type with this title already exists")
        # except Exception:
        #     await db.rollback()
        #     raise
        return setting_type

    @classmethod
    async def delete(cls, db: AsyncSession, id: int) -> None:
        try:
            setting_type = await db.get(cls, id)
            if setting_type is None:
                raise NoResultFound
            await db.delete(setting_type)
            await db.commit()
        except NoResultFound:
            print("No result found")
            raise ValueError("Setting type not found")
        except Exception:
            await db.rollback()
            raise
        return {"detail": "Setting type deleted"}
