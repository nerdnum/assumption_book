from fastapi_camelcase import CamelModel
from pydantic import Field
from pydantic_async_validation import AsyncValidationModelMixin, async_field_validator
from uuid import uuid4

from app.sqlalchemy_models.risks_impacts_sql import Severity
from app.sqlalchemy_models.risk_probabilities_sql import Probability
from app.services.database import sessionmanager
from app.pydantic_models.common_validators import (
    validate_project_id,
    validate_component_id,
    validate_user_id,
    validate_risk_type_id,
)


class RiskBase(AsyncValidationModelMixin, CamelModel):
    project_id: int | None = None
    component_id: int | None = None
    risk_type_id: int | None = None
    risk_owner_id: int | None = None
    description: str | None = None
    cause: str | None = None
    impact: str | None = None
    severity: Severity | None = None
    probability: Probability | None = None
    controls: str | None = None
    control_owner_id: int | None = None


class Risk(RiskBase):
    id: int | None = None
    uuid: str | None = None

    class Config:
        from_attributes = True


class RiskCreate(RiskBase):
    project_id: int
    component_id: int
    risk_type_id: int
    risk_owner_id: int | None = None
    description: str
    cause: str | None = None
    impact: str | None = None
    severity: Severity | None = None
    probability: Probability | None = None
    controls: str | None = None
    control_owner_id: int | None = None
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    created_by: int | None = None

    @async_field_validator("project_id")
    async def validate_project_id(self, value: int):
        result = await validate_project_id(value)

    @async_field_validator("component_id")
    async def validate_component_id(self, value: int):
        await validate_component_id(value)

    @async_field_validator("risk_type_id")
    async def validate_risk_type_id(self, value: int):
        await validate_risk_type_id(value)

    @async_field_validator("risk_owner_id")
    async def validate_risk_owner_id(self, value: int):
        await validate_user_id(value)

    @async_field_validator("control_owner_id")
    async def validate_control_owner_id(self, value: int):
        await validate_user_id(value)


class RiskUpdate(RiskBase):
    id: int | None = None
    updated_by: int | None = None

    @async_field_validator("project_id")
    async def validate_project_id(self, value: int):
        print(f"Validating project_id for update: {value}")
        if value is not None:
            await validate_project_id(value)

    @async_field_validator("component_id")
    async def validate_component_id(self, value: int):
        if value is not None:
            await validate_component_id(value)

    @async_field_validator("risk_type_id")
    async def validate_risk_type_id(self, value: int):
        if value is not None:
            await validate_risk_type_id(value)

    @async_field_validator("risk_owner_id")
    async def validate_risk_owner_id(self, value: int):
        if value is not None:
            await validate_user_id(value)

    @async_field_validator("control_owner_id")
    async def validate_control_owner_id(self, value: int):
        if value is not None:
            await validate_user_id(value)
