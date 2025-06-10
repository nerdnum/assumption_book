import enum

from sqlalchemy import String, Integer, ForeignKey, Enum, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database import BaseEntity


class Severity(enum.Enum):
    INSIGNIFICANT = 1
    MINOR = 2
    MODERATE = 3
    MAJOR = 4
    SEVERE = 5


class RiskImpact(BaseEntity):
    __tablename__ = "risk_impacts"
    risk_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("risk_types.id"))
    description: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[Severity] = mapped_column(Enum(Severity), nullable=True)

    def __repr__(cls):
        return f"<{cls.risk_type_id} - {cls.severity} - {cls.description}>"

    @classmethod
    async def get_all(cls, db) -> list["RiskImpact"]:
        all = (await db.execute(select(cls))).scalars().all()
        return all

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        risk_type_id: int,
        description: str,
        severity: Severity,
        uuid: str,
        created_by: int,
    ) -> "RiskImpact":
        try:
            db_risk_impact = cls(
                risk_type_id=risk_type_id,
                description=description,
                severity=severity,
                uuid=uuid,
                created_by=created_by,
                updated_by=created_by,
            )
            db.add(db_risk_impact)
            await db.commit()
            await db.refresh(db_risk_impact)
        except Exception as error:
            raise
        return db_risk_impact

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        id: int,
        risk_type_id: int,
        description: str,
        severity: Severity,
        updated_by: int,
    ) -> "RiskImpact":
        try:
            db_risk_impact = await db.get(cls, id)
            if not db_risk_impact:
                raise Exception("Risk impact not found")

            if risk_type_id is not None:
                db_risk_impact.risk_type_id = risk_type_id
            if description is not None:
                db_risk_impact.description = description
            if severity is not None:
                db_risk_impact.severity = severity
            db_risk_impact.updated_by = updated_by
            db_risk_impact.updated_at = db_risk_impact.updated_at

            await db.commit()
            await db.refresh(db_risk_impact)
        except Exception as error:
            raise
        return db_risk_impact

    @classmethod
    async def delete(
        cls,
        db: AsyncSession,
        id: int,
    ) -> dict:
        try:
            db_risk_impact = await db.get(cls, id)
            if not db_risk_impact:
                raise Exception("Risk impact not found")

            await db.delete(db_risk_impact)
            await db.commit()
        except Exception:
            raise
        return {"id": id, "detail": "deleted"}
