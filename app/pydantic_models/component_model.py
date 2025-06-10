from typing import Optional

from fastapi_camelcase import CamelModel
from pydantic import Field, model_validator
from pydantic.functional_validators import BeforeValidator
from pydantic_async_validation import AsyncValidationModelMixin, async_field_validator
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing_extensions import Annotated

from app.services.database import sessionmanager
from app.sqlalchemy_models.components_sql import Component as SqlComponent


def id_type_checker(value: int):
    if value < 0:
        raise ValueError("Value must be greater than or equal to 0")
    return value


TitleType = Annotated[str, Field(min_length=3, max_length=100)]
IDType = Annotated[int, BeforeValidator(id_type_checker)]


class ComponentBase(AsyncValidationModelMixin, CamelModel):
    project_id: Optional[IDType] = None
    parent_id: Optional[IDType] = None
    title: TitleType
    description: Optional[str] = None
    level: Optional[IDType] = None
    structure_code: Optional[str] = None
    sequence: Optional[IDType] = None

    async def check_for_duplicate_title_in_base(self, value: str):
        async with sessionmanager.session() as session:
            component = (
                (
                    await session.execute(
                        select(SqlComponent)
                        .where(SqlComponent.title == value)
                        .where(SqlComponent.project_id == self.project_id)
                        .where(SqlComponent.parent_id == None)
                    )
                )
                .scalars()
                .first()
            )
            if component is not None:
                raise ValueError(
                    f"A level 0 component with title '{
                    self.title}' already exists for this project"
                )

    async def check_for_duplicate_title_for_parent(self, value: str):
        async with sessionmanager.session() as session:
            component = (
                (
                    await session.execute(
                        select(SqlComponent)
                        .where(SqlComponent.title == value)
                        .where(SqlComponent.project_id == self.project_id)
                        .where(SqlComponent.parent_id == self.parent_id)
                    )
                )
                .scalars()
                .first()
            )
            if component is not None:
                raise ValueError(
                    f"A level child component with title '{
                    self.title}' already exists for this component"
                )


class ComponentCreate(ComponentBase):
    level: IDType

    @model_validator(mode="before")
    @classmethod
    def validate_model_before(cls, data: dict):
        # NB: NB use camelCase for the keys in the data dictionary
        if data.get("parentId") is not None:
            if data.get("level") == 0:
                raise ValueError("A level 0 component cannot have a parent")
        return data

    # @model_validator(mode="after")
    # def validate_model_after(self):
    #     if self.parent_id is None and self.level > 0:
    #         raise ValueError("model validator A component at levels 1 or higher must have a parent")
    #     return self

    @async_field_validator("title")
    async def check_for_duplicate_title_in_create(self, value: str):
        await self.check_for_duplicate_title_in_base(value)
        await self.check_for_duplicate_title_for_parent(value)

    @async_field_validator("parent_id")
    async def validate_component_is_unique_for_parent_id(self, value: int):
        if value is None:
            if self.level > 0:
                raise ValueError("A component at levels 1 or higher must have a parent")
        else:
            async with sessionmanager.session() as session:
                parent = (
                    (
                        await session.execute(
                            select(SqlComponent)
                            .where(SqlComponent.id == self.parent_id)
                            .options(selectinload(SqlComponent.descendants))
                        )
                    )
                    .scalars()
                    .first()
                )
                if parent is None:
                    raise ValueError("Parent component does not exist")
                if self.level == parent.level:
                    raise ValueError(
                        "A descendant component cannot be on the same level as the parent"
                    )
                if self.level != parent.level + 1:
                    raise ValueError(
                        "Component level can only be one higher than the parent level"
                    )

    ### The sequence check below prevents the reordering of components.
    ### For that reason it is disabled. The frontend should ensure that the sequences
    ### are unique and in the correct order before sending the data to the backend.

    # @async_field_validator("sequence")
    # async def check_sequence_unique(self, value: int):
    #     async with sessionmanager.session() as session:
    #         component = (
    #             (
    #                 await session.execute(
    #                     select(SqlComponent)
    #                     .where(SqlComponent.sequence == self.sequence)
    #                     .where(SqlComponent.project_id == self.project_id)
    #                     .where(SqlComponent.parent_id == self.parent_id)
    #                 )
    #             )
    #             .scalars()
    #             .first()
    #         )
    #         if component is not None:
    #             raise ValueError(
    #                 "Component with this sequence number already exists for this parent ID"
    #             )

    # @async_model_validator(mode="before")
    # async def validate_model_before(self):
    #     print("async_model_validator before")
    #     # print(self)


class ComponentUpdate(ComponentBase):
    id: Optional[IDType] = None
    uuid: Optional[str] = None
    title: Optional[TitleType] = None
    description: Optional[str] = None

    @async_field_validator("title")
    async def validate_component_title_is_unique_for_parent_id(self, value: int):
        async with sessionmanager.session() as session:
            async with sessionmanager.session() as session:
                component = (
                    (
                        await session.execute(
                            select(SqlComponent)
                            .where(SqlComponent.id != self.id)
                            .where(SqlComponent.title == value)
                            .where(SqlComponent.project_id == self.project_id)
                            .where(SqlComponent.parent_id == self.parent_id)
                        )
                    )
                    .scalars()
                    .first()
                )
                if component is not None:
                    if self.parent_id is None:
                        raise ValueError(
                            f"A level 0 component with title '{self.title}' already exists for this project"
                        )
                    else:
                        raise ValueError(
                            f"A component with title '{self.title}' already exists for the parent component"
                        )

    @async_field_validator("parent_id")
    async def validate_component_is_unique_for_parent_id(self, value: int):
        if value is not None:
            async with sessionmanager.session() as session:
                parent = (
                    (
                        await session.execute(
                            select(SqlComponent)
                            .where(SqlComponent.id == self.parent_id)
                            .options(selectinload(SqlComponent.descendants))
                        )
                    )
                    .scalars()
                    .first()
                )
                if parent is None:
                    raise ValueError("Parent component does not exist")
                if self.level == parent.level:
                    raise ValueError(
                        "A descendant component cannot be on the same level as the parent"
                    )
                if self.level != parent.level + 1:
                    raise ValueError(
                        "Component level can only be one higher than the parent level"
                    )

    ### The sequence check below prevents the reordering of components.
    ### For that reason it is disabled. The frontend should ensure that the sequences
    ### are unique and in the correct order before sending the data to the backend.

    # @async_field_validator("sequence")
    # async def check_sequence_unique(self, value: int):
    #     async with sessionmanager.session() as session:
    #         if self.parent_id is None:
    #             component = (
    #                 (
    #                     await session.execute(
    #                         select(SqlComponent)
    #                         .where(SqlComponent.sequence == self.sequence)
    #                         .where(SqlComponent.project_id == self.project_id)
    #                         .where(SqlComponent.parent_id == None)
    #                         .where(SqlComponent.id != self.id)
    #                     )
    #                 )
    #                 .scalars()
    #                 .first()
    #             )
    #         else:
    #             component = (
    #                 (
    #                     await session.execute(
    #                         select(SqlComponent)
    #                         .where(SqlComponent.sequence == self.sequence)
    #                         .where(SqlComponent.project_id == self.project_id)
    #                         .where(SqlComponent.parent_id == self.parent_id)
    #                         .where(SqlComponent.id != self.id)
    #                     )
    #                 )
    #                 .scalars()
    #                 .first()
    #             )
    #         if component is not None:
    #             raise ValueError(
    #                 "Component with this sequence number already exists for this parent ID"
    #             )


class Component(ComponentBase):
    project_id: int
    id: int
    uuid: str

    class Config:
        from_attributes = True


class ComponentWithDescendants(ComponentBase):
    id: int
    uuid: str

    descendants: Optional[list["ComponentWithDescendants"]] = []

    class Config:
        from_attributes = True


class ComponentDelete(Component):

    @async_field_validator("id")
    async def validate_component_exists(self, value: int):
        async with sessionmanager.session() as session:
            try:
                component = (
                    await session.execute(
                        select(SqlComponent)
                        .where(SqlComponent.id == self.id)
                        .options(selectinload(SqlComponent.descendants))
                    )
                ).scalar_one()
                if len(component.descendants) > 0:
                    raise ValueError("Cannot delete a component with descendants")
            except Exception as error:
                raise error
