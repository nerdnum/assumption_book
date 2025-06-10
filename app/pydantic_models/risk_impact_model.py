from fastapi_camelcase import CamelModel
from pydantic import Field
from uuid import uuid4
from app.sqlalchemy_models.risks_impacts_sql import Severity


class RiskImpactBase(CamelModel):
    risk_type_id: int | None = None
    description: str | None = None
    severity: Severity | None = None


class RiskImpactCreate(RiskImpactBase):
    risk_type_id: int
    description: str
    severity: Severity
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    created_by: int | None = None


class RiskImpactUpdate(RiskImpactBase):
    id: int | None = None
    updated_by: int | None = None


class RiskImpact(RiskImpactBase):
    id: int | None = None
    uuid: str | None = None
    created_by: int | None = None
    updated_by: int | None = None

    class Config:
        from_attributes = True
