from fastapi_camelcase import CamelModel
from pydantic import Field
from uuid import uuid4

from app.sqlalchemy_models.risk_probabilities_sql import Probability


class RiskProbabilityBase(CamelModel):
    probability: Probability | None = None
    percentage_min: float | None = None
    percentage_max: float | None = None
    frequency: float | None = None
    explanation: str | None = None
    experience: str | None = None


class RiskProbabilityCreate(RiskProbabilityBase):
    probability: Probability
    percentage_min: float
    percentage_max: float
    frequency: float
    explanation: str | None = None
    experience: str | None = None
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    created_by: int | None = None


class RiskProbabilityUpdate(RiskProbabilityBase):
    id: int | None = None
    updated_by: int | None = None


class RiskProbability(RiskProbabilityBase):
    id: int | None = None
    uuid: str | None = None
    created_by: int | None = None
    updated_by: int | None = None

    class Config:
        from_attributes = True
