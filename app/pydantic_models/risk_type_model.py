from fastapi_camelcase import CamelModel
from pydantic import Field
from uuid import uuid4
from typing import Optional


class RiskTypeBase(CamelModel):
    title: str | None = None
    abbreviation: str | None = None
    description: str | None = None


class RiskTypeCreate(RiskTypeBase):
    title: str
    abbreviation: str
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    created_by: int | None = None


class RiskTypeUpdate(RiskTypeBase):
    id: int | None = None
    updated_by: int | None = None


class RiskType(RiskTypeBase):
    id: int | None = None
    uuid: str | None = None
    created_by: int | None = None
    updated_by: int | None = None

    class Config:
        from_attributes = True
