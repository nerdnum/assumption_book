from uuid import uuid4

from sqlalchemy import CheckConstraint, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.services.database import BaseEntity
from typing import Any


class RiskType(BaseEntity):
    __tablename__ = "risk_types"

    title: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    abbreviation: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    __table_args__ = (
        CheckConstraint("length(title) > 0", name="title_length"),
        CheckConstraint(
            "length(abbreviation) >= 2 and length(abbreviation) <= 5",
            name="abbreviation_length",
        ),
    )

    @validates("abbreviation")
    def validate_abbreviation(self, key: str, value: str) -> str:
        print("Validating abbreviation", key, value)
        if value:
            return value.upper()
        return value

    def __repr__(cls):
        return f"<{cls.abbreviation} - {cls.title}>"

    @classmethod
    async def get_all(cls, db):
        all = (await db.execute(select(cls))).scalars().all()
        return all

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        title: str,
        abbreviation: str,
        description: str,
        uuid: str,
        created_by: int,
    ) -> "RiskType":
        try:
            db_risk_type = cls(
                title=title,
                abbreviation=abbreviation,
                description=description,
                uuid=uuid,
                created_by=created_by,
                updated_by=created_by,
            )
            db.add(db_risk_type)
            await db.commit()
            await db.refresh(db_risk_type)
        except Exception as error:
            raise
        return db_risk_type

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        id: int,
        title: str,
        abbreviation: str,
        description: str,
        updated_by: int,
    ) -> "RiskType":
        try:
            db_risk_type = await db.get(cls, id)
            if not db_risk_type:
                raise ValueError("Risk type not found")

            if title:
                db_risk_type.title = title
            if abbreviation:
                db_risk_type.abbreviation = abbreviation
            if description:
                db_risk_type.description = description
            db_risk_type.updated_by = updated_by

            await db.commit()
            await db.refresh(db_risk_type)
        except Exception as error:
            raise
        return db_risk_type

    @classmethod
    async def delete(cls, db: AsyncSession, id: int) -> dict:
        try:
            db_risk_type = await db.get(cls, id)
            if not db_risk_type:
                raise ValueError("Risk type not found")
            await db.delete(db_risk_type)
            await db.commit()
        except Exception as error:
            raise
        return {"id": id, "detail": "deleted"}
