from enum import Enum

from sqlalchemy import String, Integer, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import ENUM as PG_enum

from app.services.database import BaseEntity
from app.sqlalchemy_models.risks_impacts_sql import Severity
from app.sqlalchemy_models.risk_probabilities_sql import Probability


class Risk(BaseEntity):
    __tablename__ = "risks"
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"))
    component_id: Mapped[int] = mapped_column(Integer, ForeignKey("components.id"))
    risk_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("risk_types.id"))
    risk_owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    description: Mapped[str] = mapped_column(String, nullable=False)
    cause: Mapped[str] = mapped_column(String, nullable=True)
    impact: Mapped[str] = mapped_column(String, nullable=True)
    severity: Mapped[Severity] = mapped_column(PG_enum(Severity), nullable=True)
    probability: Mapped[Probability] = mapped_column(
        PG_enum(Probability), nullable=True
    )
    controls: Mapped[str] = mapped_column(String, nullable=True)
    control_owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    def __repr__(cls):
        return f"<{cls.risk_type_id} - {cls.severity} - {cls.description}>"

    @classmethod
    async def get_all(cls, db) -> list["Risk"]:
        all = (await db.execute(select(cls))).scalars().all()
        return all

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        project_id: int,
        component_id: int,
        risk_type_id: int,
        risk_owner_id: int,
        description: str,
        cause: str,
        impact: str,
        severity: Severity,
        probability: Probability,
        controls: str,
        control_owner_id: int,
        uuid: str,
        created_by: int,
    ) -> "Risk":
        try:
            db_risk = cls(
                project_id=project_id,
                component_id=component_id,
                risk_type_id=risk_type_id,
                risk_owner_id=risk_owner_id,
                description=description,
                cause=cause,
                impact=impact,
                severity=severity,
                probability=probability,
                controls=controls,
                control_owner_id=control_owner_id,
                uuid=uuid,
                created_by=created_by,
                updated_by=created_by,
            )
            db.add(db_risk)
            await db.commit()
            await db.refresh(db_risk)
        except Exception as error:
            raise
        return db_risk

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        id: int,
        project_id: int,
        component_id: int,
        risk_type_id: int,
        risk_owner_id: int,
        description: str,
        cause: str,
        impact: str,
        severity: Severity,
        probability: Probability,
        controls: str,
        control_owner_id: int,
        updated_by: int,
    ) -> "Risk":
        try:
            db_risk = await db.get(cls, id)
            if not db_risk:
                raise Exception("Risk not found")
            if project_id is not None:
                db_risk.project_id = project_id
            if component_id is not None:
                db_risk.component_id = component_id
            if risk_type_id is not None:
                db_risk.risk_type_id = risk_type_id
            if risk_owner_id is not None:
                db_risk.risk_owner_id = risk_owner_id
            if description is not None:
                db_risk.description = description
            if cause is not None:
                db_risk.cause = cause
            if impact is not None:
                db_risk.impact = impact
            if severity is not None:
                db_risk.severity = severity
            if probability is not None:
                db_risk.probability = probability
            if controls is not None:
                db_risk.controls = controls
            if control_owner_id is not None:
                db_risk.control_owner_id = control_owner_id
            db_risk.updated_by = updated_by

            await db.commit()
            await db.refresh(db_risk)
        except Exception as error:
            raise
        return db_risk

    @classmethod
    async def delete(
        cls,
        db: AsyncSession,
        id: int,
    ) -> dict:
        try:
            db_risk = await db.get(cls, id)
            if not db_risk:
                raise Exception("Risk not found")
            await db.delete(db_risk)
            await db.commit()
        except Exception as error:
            raise
        return {"id": id, "details": "deleted"}
