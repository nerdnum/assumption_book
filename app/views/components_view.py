import os

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic_async_validation.fastapi import ensure_request_validation_errors
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated


from app.views.auth_view import get_current_user_with_roles
from app.sqlalchemy_models.user_project_role_sql import User as SqlUser
from app.html2docx.htmldocx import HtmlToDocx
from app.pydantic_models.component_model import (
    Component,
    ComponentCreate,
    ComponentDelete,
    ComponentUpdate,
    ComponentWithDescendants,
)
from app.services.database import get_db
from app.services.utils import pretty_print
from app.sqlalchemy_models.components_sql import Component as SqlComponent


router = APIRouter(prefix="/components", tags=["components"])


# @router.get("/templates/", response_model=list[Component])
# async def get_all_templates(db: AsyncSession = Depends(get_db)) -> list[Component]:
#     components = await SqlComponent.get_all_templates(db)
#     return components


async def get_descendants(
    db: AsyncSession,
    component_id: int,
    recursion_level: int = 10,
    level: int = 0,
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> list[dict]:
    descendants = []
    if level < recursion_level:
        level += 1
        components = (
            (
                await db.execute(
                    select(SqlComponent).where(SqlComponent.parent_id == component_id)
                )
            )
            .scalars()
            .all()
        )
        for component in components:
            component_dict = Component.model_validate(component).model_dump()
            component_dict["descendants"] = await get_descendants(
                db, component.id, recursion_level, level
            )
            descendants.append(component_dict)
    else:
        raise ValueError("Recursion level of 10 exceeded")
    return descendants


async def get_component_hierarchy(
    component_id: int,
    levels: int = 1,
    db: AsyncSession = Depends(get_db),
) -> list[ComponentWithDescendants]:
    component = await SqlComponent.get_by_id(db, component_id)
    component_dict = Component.model_validate(component).model_dump()
    component_dict["descendants"] = await get_descendants(db, component.id, levels, 0)
    return component_dict


async def get_root_component_hierarchy(
    project_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[ComponentWithDescendants]:
    component_list = []
    root_components = await SqlComponent.get_root_components(db, project_id)
    for component in root_components:
        component_dict = Component.model_validate(component).model_dump()
        descendants = await get_descendants(db, component.id, 10, 0)
        component_dict["descendants"] = descendants
        component_list.append(component_dict)
    return component_list


@router.get("", response_model=list[Component])
async def get_components(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> list[Component]:
    # Ok as on 2024-06-25 11:50
    components = await SqlComponent.get_all(db, project_id)
    return components


@router.get("/root-components", response_model=list[Component])
async def root_components(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> list[Component]:
    # Ok as on 2024-06-25 11:53
    root_components = await SqlComponent.get_root_components(db, project_id)
    return root_components


@router.get("/hierarchy", response_model=list[ComponentWithDescendants])
async def get_hierarchy(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> list[ComponentWithDescendants]:
    # Ok as on 2024-06-25 11:53
    hierarchy = await get_root_component_hierarchy(project_id, db)
    return hierarchy


@router.get("/{component_id:int}/descendants", response_model=list[Component])
async def get_component_by_id_with_descendants(
    project_id: int,
    component_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> list[Component]:
    try:
        descendants = await get_descendants(db, component_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return descendants


@router.get("/{component_id:int}/html", response_model=str)
async def get_component_html_by_id(
    component_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> str:
    try:
        component_html = await SqlComponent.get_html_by_id(db, component_id)
        parser = HtmlToDocx()
        parser.table_style = "Colorful Grid Accent 1"
        docx = parser.parse_html_string(component_html)
        cwd = os.getcwd()
        store_path = os.path.join(
            cwd, "app", "static", f"component_{component_id}.docx"
        )
        docx.save(store_path)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return component_html


@router.get("/{component_id:int}", response_model=Component)
async def get_component(
    project_id: int,
    component_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> Component:
    try:
        component = await SqlComponent.get_by_id(db, component_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return component


@router.post(
    "/{parent_id:int}", response_model=Component, status_code=status.HTTP_201_CREATED
)
async def create_component_by_parent_id(
    project_id: int,
    parent_id: int,
    component: ComponentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> Component:
    # For level 1 components and above

    try:
        if component.project_id is None:
            component.project_id = project_id
        else:
            if component.project_id != project_id:
                raise ValueError(
                    "Project ID in json body does not match project ID in URL"
                )
        if component.parent_id is None:
            component.parent_id = parent_id
        if component.level == 0:
            raise ValueError("A level 0 component cannot have a parent ID")
        elif component.parent_id != parent_id:
            raise ValueError("Parent ID in json body does not match parent ID in URL")
        else:
            component.parent_id = parent_id
        component.created_by = current_user.id
        component.updated_by = current_user.id
        with ensure_request_validation_errors("body"):
            await component.model_async_validate()
        component = await SqlComponent.create(db, **component.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return component


@router.post("", response_model=Component, status_code=status.HTTP_201_CREATED)
async def create_component(
    project_id: int,
    component: ComponentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> Component:
    try:
        if component.project_id is None:
            component.project_id = project_id
        elif component.project_id != project_id:
            raise ValueError("Project ID in json body does not match project ID in URL")
        with ensure_request_validation_errors("body"):
            await component.model_async_validate()
        component = await SqlComponent.create(
            db, **component.model_dump(), user_id=current_user.id
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return component


@router.put("/{component_id:int}", response_model=Component)
async def update_component_by_id(
    project_id: int,
    component_id: int,
    component: ComponentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> Component:
    try:
        sql_component_to_update = await SqlComponent.get_by_id(db, component_id)
        if sql_component_to_update is None:
            raise ValueError("Component does not exist")
        model_to_update = Component.model_validate(sql_component_to_update)
        dict_to_update = model_to_update.model_dump()
        for key, value in component.model_dump().items():
            if value is not None:
                dict_to_update[key] = value
        updated_component = ComponentUpdate(**dict_to_update)
        with ensure_request_validation_errors("body"):
            await updated_component.model_async_validate()
        component = await SqlComponent.update(
            db, component_id, **updated_component.model_dump(), user_id=current_user.id
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return component


@router.delete("/{component_id:int}", response_model=Component)
async def delete_component(
    component_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> Component:
    try:
        component = await SqlComponent.get_by_id(db, component_id)
        component_dict = {
            "id": component.id,
            "uuid": component.uuid,
            "title": component.title,
            "description": component.description,
            "level": component.level,
            "sequence": component.sequence,
            "project_id": component.project_id,
            "parent_id": component.parent_id,
        }

        try:
            delete_component = ComponentDelete(**component_dict)
            with ensure_request_validation_errors("body"):
                await delete_component.model_async_validate()
            await SqlComponent.delete(db, component_id)
            await db.commit()
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return component
