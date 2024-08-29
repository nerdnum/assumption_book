from typing import Any, Dict

from fastapi_camelcase import CamelModel
from pydantic_async_validation import AsyncValidationModelMixin, async_field_validator
from sqlalchemy import select

from app.services.database import sessionmanager
from app.sqlalchemy_models.components_sql import Component as SqlComponent
from app.sqlalchemy_models.projects_sql import Project as SqlProject


class DocumentBase(CamelModel):
    project_id: int
    component_id: int
    title: str
    sequence: int


class DocumentCreate(DocumentBase):
    content: Dict[Any, Any]


class DocumentCreateResponse(DocumentBase):
    id: int
    uuid: str


class Document(DocumentBase):
    id: int
    uuid: str
    content: Dict[Any, Any]

    class Config:
        from_attributes = True

    @async_field_validator("project_id")
    async def check_if_project_exists(self, value: int):
        async with sessionmanager.session() as session:
            try:
                (
                    await session.execute(
                        select(SqlProject).where(SqlProject.id == self.value)
                    )
                ).scalars().first()
            except ValueError as error:
                raise error
