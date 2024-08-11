from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_async_validation.fastapi import ensure_request_validation_errors
from typing import Union

from app.services.database import sessionmanager, get_db
from app.pydantic_models.component_model import Component, ComponentCreate, ComponentUpdate, ComponentWithDescendants, ComponentDelete
from app.sqlalchemy_models.components_sql import Component as SqlComponent
from app.sqlalchemy_models.projects_sql import Project as SqlProject


router = APIRouter(prefix="/components", tags=["components"])


# @router.get("/templates/", response_model=list[Component])
# async def get_all_templates(db: AsyncSession = Depends(get_db)) -> list[Component]:
#     components = await SqlComponent.get_all_templates(db)
#     return components


@router.get("", response_model=list[Component])
async def get_components(project_slug: str, db: AsyncSession = Depends(get_db)) -> list[Component]:
    project_id = await SqlProject.get_id_by_slug(db, project_slug)
    components = await SqlComponent.get_all(db, project_id)
    return components


@router.get("/hierarchy", response_model=list[ComponentWithDescendants])
async def get_hierarchy(project_slug: str, db: AsyncSession = Depends(get_db)) -> list[ComponentWithDescendants]:
    project_id = await SqlProject.get_id_by_slug(db, project_slug)
    hierarchy = await SqlComponent.get_hierarchy(db, project_id, 0)
    return hierarchy


@router.post("/{parent_id:int}", response_model=Component, status_code=status.HTTP_201_CREATED)
async def create_component_by_parent_id(project_slug: str, parent_id: int, component: ComponentCreate, db: AsyncSession = Depends(get_db)) -> Component:
    try:
        project_id = await SqlProject.get_id_by_slug(db, project_slug)
        component.parent_id = parent_id
        with ensure_request_validation_errors("body"):
            await component.model_async_validate()
        component = await SqlComponent.create(db, **component.model_dump())
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@router.post("/{parent_slug:str}", response_model=Component, status_code=status.HTTP_201_CREATED)
async def create_component_by_parent_slug(project_slug: str, parent_slug: str, component: ComponentCreate, db: AsyncSession = Depends(get_db)) -> Component:
    try:
        project_id = await SqlProject.get_id_by_slug(db, project_slug)
        parent_id = SqlComponent.get_id_by_slug(db, project_id, parent_slug)
        if component.parent_id is None:
            component.parent_id = parent_id
        with ensure_request_validation_errors("body"):
            await component.model_async_validate()
        component = await SqlComponent.create(db, **component.model_dump())
    except ValueError as error:
        print('Value error raised')
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@router.post("", response_model=Component, status_code=status.HTTP_201_CREATED)
async def create_component(project_slug: str, component: ComponentCreate, db: AsyncSession = Depends(get_db)) -> Component:
    # For level 0 component items
    try:
        if component.project_id is None:
            project_id = await SqlProject.get_id_by_slug(db, project_slug)
        component.project_id = project_id
        with ensure_request_validation_errors("body"):
            await component.model_async_validate()
        component = await SqlComponent.create(db, **component.model_dump())
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@router.get("/{component_id:int}", response_model=Component)
async def get_component(project_slug: str, component_id: int, db: AsyncSession = Depends(get_db)) -> Component:
    # Component ID is unique across all projects, so project_slug is irrelavant
    try:
        component = await SqlComponent.get_by_id(db, component_id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@router.get("/{component_slug:str}", response_model=Component)
async def get_component(project_slug: str, component_slug: str, db: AsyncSession = Depends(get_db)) -> Component:
    # Component slug is not unique across all projects, so project_slug is relavant
    project_id = await SqlProject.get_id_by_slug(db, project_slug)
    try:
        component = await SqlComponent.get_by_slug(db, project_id, component_slug)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@ router.get("/{component_id:int}/with-descendants", response_model=ComponentWithDescendants)
async def get_component_by_id_with_descendants(project_slug: str, component_id: int, db: AsyncSession = Depends(get_db)) -> ComponentWithDescendants:
    # Component ID is unique across all projects, so project_slug is irrelavant
    try:
        component = await SqlComponent.get_with_descendants_by_id(db, component_id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@ router.get("/{component_slug:str}/with-descendants", response_model=ComponentWithDescendants)
async def get_component_by_slug_with_descendants(project_slug: str, component_slug: str, db: AsyncSession = Depends(get_db)) -> ComponentWithDescendants:
    project_id = await SqlProject.get_id_by_slug(db, project_slug)
    component_id = await SqlComponent.get_id_by_slug(db, project_id, component_slug)
    try:
        component = await SqlComponent.get_with_descendants_by_id(db, project_id, component_id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@ router.put("/{component_id:int}", response_model=Component)
async def update_component(component_id: int, component: ComponentUpdate, db: AsyncSession = Depends(get_db)) -> Component:
    try:
        component = await SqlComponent.update(db, component_id, **component.model_dump())
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@ router.delete("/{component_id:int}", response_model=Component)
async def delete_component(component_id: int, db: AsyncSession = Depends(get_db)) -> Component:
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

            raise HTTPException(
                status_code=400, detail=str(error))
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component
