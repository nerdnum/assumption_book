from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    select,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.services.database import BaseEntity
from app.sqlalchemy_models.setting_types_sql import SettingType


class Setting(BaseEntity):
    __tablename__ = "settings"

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    value: Mapped[JSON] = mapped_column(JSON, nullable=True)
    setting_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting_types.id"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(setting_type_id, title),
        CheckConstraint("length(title) > 0", name="title_length"),
    )

    @classmethod
    async def get_all(cls, db):
        return (await db.execute(select(cls))).scalars().all()

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        title: str,
        description: str | None,
        value: str,
        setting_type_id: int,
        user_id: int | None = None,
    ) -> "Setting":

        setting = cls(
            title=title,
            description=description,
            value=value,
            setting_type_id=setting_type_id,
            uuid=str(uuid4()),
            created_by=user_id,
            updated_by=user_id,
        )

        setting_type = await SettingType.get(db, setting_type_id)
        if setting_type is None:
            raise ValueError("Setting type not found")

        try:
            db.add(setting)
            await db.commit()
            await db.refresh(setting)

        except Exception as error:
            await db.rollback()
            error_str = str(error)
            if (
                error_str.find(
                    'duplicate key value violates unique constraint "settings_value_title_key"'
                )
                != -1
            ):
                raise ValueError("Setting already exists")
            if (
                error_str.find(
                    'duplicate key value violates unique constraint "settings_setting_type_id_title_key"'
                )
                != -1
            ):
                raise ValueError("Setting already exists")
            if (
                error_str.find(
                    'new row for relation "settings" violates check constraint "title_length"'
                )
                != -1
            ):
                raise ValueError("Title field cannot be empty")
            raise
        return setting

    @classmethod
    async def get(cls, db: AsyncSession, id: int) -> "Setting":
        try:
            setting = await db.get(cls, id)
            if setting is None:
                raise NoResultFound
        except NoResultFound:
            raise ValueError("Setting not found")
        except Exception:
            raise
        return setting

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        id: int,
        title: str | None,
        description: str | None,
        value: str | None,
        setting_type_id: int | None,
        user_id: int | None = None,
    ) -> "Setting":
        try:

            setting = await db.get(cls, id)
            if setting is None:
                raise NoResultFound

            if title is not None:
                setting.title = title

            if description is not None:
                setting.description = description

            if value is not None:
                setting.value = value

            if setting_type_id is not None:
                setting_type = await SettingType.get(db, setting_type_id)
                if setting_type is None:
                    raise ValueError("Setting type not found")
                setting.setting_type_id = setting_type_id

            if user_id is not None:
                setting.updated_by = user_id

            await db.commit()
            await db.refresh(setting)

        except NoResultFound:
            raise ValueError("Setting not found")
        except Exception as error:
            await db.rollback()
            error_str = str(error)
            if (
                error_str.find(
                    'duplicate key value violates unique constraint "settings_value_title_key"'
                )
                != -1
            ):
                raise ValueError("Setting already exists")
            if (
                error_str.find(
                    'duplicate key value violates unique constraint "settings_setting_type_id_title_key"'
                )
                != -1
            ):
                raise ValueError("Setting already exists")
            if (
                error_str.find(
                    'new row for relation "settings" violates check constraint "title_length"'
                )
                != -1
            ):
                raise ValueError("Title field cannot be empty")
            raise
        return setting

    @classmethod
    async def delete(cls, db: AsyncSession, id: int) -> None:
        try:
            setting = await db.get(cls, id)
            if setting is None:
                raise NoResultFound
            await db.delete(setting)
            await db.commit()
        except NoResultFound:
            raise ValueError("Setting not found")
        except Exception:
            raise
        return {"detail": "Setting deleted"}
