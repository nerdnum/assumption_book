import uuid
from typing import Annotated, Any, Dict, List, Optional

from fastapi_camelcase import CamelModel
from pydantic import ConfigDict, field_validator, model_validator
from pydantic_async_validation import AsyncValidationModelMixin, async_field_validator
from sqlalchemy import select
from typing_extensions import Self

from app.services.database import sessionmanager
from app.services.utils import pretty_print
from app.sqlalchemy_models.components_sql import Component as SqlComponent
from app.sqlalchemy_models.documents_sql import Document as SqlDocument
from app.sqlalchemy_models.projects_sql import Project as SqlProject


class AttrsContent(CamelModel):
    __pydantic_extra__: Dict[Any, Any]
    id: str

    @field_validator("id")
    @classmethod
    def validate_attrs_id(cls, value: str):
        try:
            uuid.UUID(value, version=4)
        except ValueError:
            raise ValueError("The 'id' must be a valid UUID")
        return value

    model_config = ConfigDict(extra="allow")


class SubContent(CamelModel):
    type: str
    attrs: AttrsContent
    content: Optional[List[Any]] = None

    # @model_validator(mode="before")
    # @classmethod
    # def check_data_checksum(cls, data: Any) -> Any:
    #     pretty_print(data["content"])
    #     print(data["attrs"]["checksum"])
    #     md5 = hashlib.md5()
    #     md5.update(json.dumps(data["content"]).encode("utf-16"))
    #     print(md5.hexdigest())
    #     # if isinstance(data, dict):
    #     #     assert "card_number" not in data, "card_number should not be included"
    #     return data

    # @field_validator("type")
    # @classmethod
    # def validate_attrs_id(cls, value: int):
    #     print("subcontent: Checking content type")
    #     return value

    # @field_validator("attrs")
    # @classmethod
    # def validate_attrs_id(cls, value: dict):
    #     if "id" not in value.keys():
    #         raise ValueError("The 'attrs' object must contain and 'id'")
    #     return value


class Content(CamelModel):
    type: str
    context: str
    content: List[SubContent]

    # @field_validator("type")
    # @classmethod
    # def validate_attrs_id(cls, value: int):
    #     print("Content: Checking content type")
    #     return value


class DocumentBase(AsyncValidationModelMixin, CamelModel):
    project_id: int
    component_id: int
    title: str
    sequence: int

    async def check_for_duplicate_title_in_base(self, value: str):
        async with sessionmanager.session() as session:
            document = (
                (
                    await session.execute(
                        select(SqlDocument)
                        .where(SqlDocument.title == value)
                        .where(SqlDocument.project_id == self.project_id)
                        .where(SqlDocument.component_id == self.component_id)
                    )
                )
                .scalars()
                .first()
            )
            if document is not None:
                raise ValueError(
                    f"A document with title '{self.title}' already exists for this component"
                )

    async def check_project_id_exist_in_base(self, value: str):
        async with sessionmanager.session() as session:
            project = (
                (
                    await session.execute(
                        select(SqlProject).where(SqlProject.id == self.project_id)
                    )
                )
                .scalars()
                .first()
            )
            if project is None:
                raise ValueError("Project not found")

    async def check_component_id_exist_in_base(self, value: int):
        async with sessionmanager.session() as session:
            project = (
                (
                    await session.execute(
                        select(SqlComponent).where(SqlComponent.id == value)
                    )
                )
                .scalars()
                .first()
            )
            if project is None:
                raise ValueError("Component not found")


class DocumentCreate(DocumentBase):
    content: Content

    @async_field_validator("title")
    async def check_for_duplicate_title_in_create(self, value: str):
        await self.check_for_duplicate_title_in_base(value)

    @async_field_validator("project_id")
    async def check_project_id_exist_in_create(self, value: int):
        await self.check_project_id_exist_in_base(value)

    @async_field_validator("component_id")
    async def check_component_id_exist_in_create(self, value: int):
        await self.check_component_id_exist_in_base(value)


class DocumentCreateResponse(DocumentBase):
    id: int
    uuid: str
    content: Content


class Document(DocumentBase):
    id: int
    uuid: str
    content: Content

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    def verify_square(self) -> Self:
        return self

    # @async_field_validator("project_id")
    # async def check_if_project_exists(self, value: int):
    #     async with sessionmanager.session() as session:
    #         try:
    #             (
    #                 await session.execute(
    #                     select(SqlProject).where(SqlProject.id == self.value)
    #                 )
    #             ).scalars().first()
    #         except ValueError as error:
    #             raise error
