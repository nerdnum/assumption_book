import enum

from sqlalchemy import String, Float, ForeignKey, Enum, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database import BaseEntity


class Probability(enum.Enum):
    UNLIKELY = 1
    POSSIBLE = 2
    LIKELY = 3
    PROBABLE = 4
    CERTAIN = 5


class RiskProbability(BaseEntity):
    __tablename__ = "risk_probabilities"
    probability: Mapped[Probability] = mapped_column(Enum(Probability), nullable=False)
    percentage_min: Mapped[float] = mapped_column(Float, nullable=False)
    percentage_max: Mapped[float] = mapped_column(Float, nullable=False)
    frequency: Mapped[float] = mapped_column(Float, nullable=False)
    explanation: Mapped[str] = mapped_column(String)
    experience: Mapped[str] = mapped_column(String)

    def __repr__(cls):
        return f"<{cls.probability} - {cls.percentage_min}% - {cls.percentage_max}%>"

    @classmethod
    async def get_all(cls, db) -> list["RiskProbability"]:
        all = (await db.execute(select(cls))).scalars().all()
        return all

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        probability: int,
        percentage_min: float,
        percentage_max: float,
        frequency: float,
        explanation: str,
        experience: str,
        uuid: str,
        created_by: int,
    ) -> "RiskProbability":
        try:
            db_risk_probability = cls(
                probability=probability,
                percentage_min=percentage_min,
                percentage_max=percentage_max,
                frequency=frequency,
                explanation=explanation,
                experience=experience,
                uuid=uuid,
                created_by=created_by,
                updated_by=created_by,
            )
            db.add(db_risk_probability)
            await db.commit()
            await db.refresh(db_risk_probability)
        except Exception as error:
            raise
        return db_risk_probability

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        id: int,
        probability: int,
        percentage_min: float,
        percentage_max: float,
        frequency: float,
        explanation: str,
        experience: str,
        updated_by: int,
        uuid: str | None = None,
    ) -> "RiskProbability":
        try:
            db_risk_probability = await db.get(cls, id)
            if not db_risk_probability:
                raise Exception("Risk impact not found")

            if probability is not None:
                db_risk_probability.probability = probability
            if percentage_min is not None:
                db_risk_probability.percentage_min = percentage_min
            if percentage_max is not None:
                db_risk_probability.percentage_max = percentage_max
            if frequency is not None:
                db_risk_probability.frequency = frequency
            if explanation is not None:
                db_risk_probability.explanation = explanation
            if experience is not None:
                db_risk_probability.experience = experience
            db_risk_probability.updated_by = updated_by

            await db.commit()
            await db.refresh(db_risk_probability)
        except Exception as error:
            raise
        return db_risk_probability

    @classmethod
    async def delete(
        cls,
        db: AsyncSession,
        id: int,
    ) -> dict:
        try:
            db_risk_probability = await db.get(cls, id)
            if not db_risk_probability:
                raise Exception("Risk probability not found")

            await db.delete(db_risk_probability)
            await db.commit()
        except Exception:
            raise
        return {"id": id, "detail": "deleted"}
