from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_async_validation.fastapi import ensure_request_validation_errors
from slugify import slugify

from app.services.database import sessionmanager, get_db
from app.pydantic_models.component_model import Component, ComponentCreate, ComponentUpdate, ComponentWithDescendants, ComponentDelete
from app.sqlalchemy_models.components_sql import Component as SqlComponent
from app.sqlalchemy_models.projects_sql import Project as SqlProject


router = APIRouter(prefix="/components", tags=["components"])


# @router.get("/templates/", response_model=list[Component])
# async def get_all_templates(db: AsyncSession = Depends(get_db)) -> list[Component]:
#     components = await SqlComponent.get_all_templates(db)
#     return components


async def get_descendants(db: AsyncSession, component_id: int, recursion_level: 10, level: int = 0) -> list[dict]:
    descendants = []
    if level < recursion_level:
        level += 1
        components = (await db.execute(
            select(SqlComponent).where(SqlComponent.parent_id == component_id))).scalars().all()
        for component in components:
            component_dict = Component.model_validate(component).model_dump()
            component_dict["descendants"] = await get_descendants(db, component.id, recursion_level, level)
            descendants.append(component_dict)
    return descendants


async def get_component_hierarchy(component_id: int, levels: int = 1, db: AsyncSession = Depends(get_db)) -> list[ComponentWithDescendants]:
    component = await SqlComponent.get_by_id(db, component_id)
    component_dict = Component.model_validate(component).model_dump()
    component_dict["descendants"] = await get_descendants(db, component.id, levels, 0)
    return component_dict


async def get_root_component_hierarchy(project_id: int, db: AsyncSession = Depends(get_db)) -> list[ComponentWithDescendants]:
    component_list = []
    root_components = await SqlComponent.get_root_components(db, project_id)
    for component in root_components:
        component_dict = Component.model_validate(component).model_dump()
        component_dict["descendants"] = await get_descendants(db, component.id, 10, 0)
        component_list.append(component_dict)
    return component_list


@router.get("", response_model=list[Component])
async def get_components(project_id: int, db: AsyncSession = Depends(get_db)) -> list[Component]:
    # Ok as on 2024-06-25 11:50
    components = await SqlComponent.get_all(db, project_id)
    return components


@router.get("/root-components", response_model=list[Component])
async def root_components(project_id: int, db: AsyncSession = Depends(get_db)) -> list[Component]:
    # Ok as on 2024-06-25 11:53
    root_components = await SqlComponent.get_root_components(db, project_id)
    return root_components


@router.get("/hierarchy", response_model=list[ComponentWithDescendants])
async def get_hierarchy(project_id: int, db: AsyncSession = Depends(get_db)) -> list[ComponentWithDescendants]:
    # Ok as on 2024-06-25 11:53
    hierarchy = await get_root_component_hierarchy(project_id, db)
    return hierarchy


@router.get("/{component_id:int}", response_model=Component)
async def get_component(project_id: int, component_id: int, db: AsyncSession = Depends(get_db)) -> Component:
    try:
        component = await SqlComponent.get_by_id(db, component_id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@router.post("/{parent_id:int}", response_model=Component, status_code=status.HTTP_201_CREATED)
async def create_component_by_parent_id(project_id: int, parent_id: int, component: ComponentCreate, db: AsyncSession = Depends(get_db)) -> Component:
    # For level 1 components and above

    try:
        if component.project_id is None:
            component.project_id = project_id
        else:
            if component.project_id != project_id:
                raise ValueError(
                    "Project ID in json body does not match project ID in URL")
        if component.parent_id is None:
            component.parent_id = parent_id
        if component.level == 0:
            raise ValueError(
                "A level 0 component cannot have a parent ID")
        elif component.parent_id != parent_id:
            raise ValueError(
                "Parent ID in json body does not match parent ID in URL")
        else:
            component.parent_id = parent_id
        if component.slug is None:
            component.slug = slugify(component.title)
        with ensure_request_validation_errors("body"):
            await component.model_async_validate()
        component = await SqlComponent.create(db, **component.model_dump())
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@router.post("/{parent_slug:str}", response_model=Component, status_code=status.HTTP_201_CREATED)
async def create_component_by_parent_slug(project_id: int, parent_slug: str, component: ComponentCreate, db: AsyncSession = Depends(get_db)) -> Component:
    # For level 1 compomnents and above
    try:
        if component.project_id is None:
            component.project_id = project_id
        parent_id = SqlComponent.get_id_by_slug(db, parent_slug)
        if component.parent_id is None:
            component.parent_id = parent_id
        if component.slug is None:
            component.slug = slugify(component.title)
        with ensure_request_validation_errors("body"):
            await component.model_async_validate()
        component = await SqlComponent.create(db, **component.model_dump())
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@router.post("", response_model=Component, status_code=status.HTTP_201_CREATED)
async def create_component(project_id: int, component: ComponentCreate, db: AsyncSession = Depends(get_db)) -> Component:
    try:
        if component.project_id is None:
            component.project_id = project_id
        elif component.project_id != project_id:
            raise ValueError(
                "Project ID in json body does not match project ID in URL")
        if component.slug is None:
            component.slug = slugify(component.title)
        with ensure_request_validation_errors("body"):
            await component.model_async_validate()
        component = await SqlComponent.create(db, **component.model_dump())
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@router.get("/{component_slug:str}", response_model=Component)
async def get_component(project_id: int, component_slug: str, db: AsyncSession = Depends(get_db)) -> Component:
    try:
        component = await SqlComponent.get_by_slug(db, project_id, component_slug)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@ router.get("/{component_id:int}/descendants", response_model=list[Component])
async def get_component_by_id_with_descendants(project_id: int, component_id: int, db: AsyncSession = Depends(get_db)) -> list[Component]:
    try:
        descendants = await SqlComponent.get_descendants(db, component_id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return descendants


@ router.get("/{component_slug:str}/descendants", response_model=list[Component])
async def get_component_by_slug_with_descendants(project_id: int, component_slug: str, db: AsyncSession = Depends(get_db)) -> list[Component]:
    try:
        component_id = await SqlComponent.get_id_by_slug(db, project_id, component_slug)
        component = await SqlComponent.get_with_descendants_by_slug(db, project_id, component_id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@ router.get("/{component_id:int}/with-descendants", response_model=ComponentWithDescendants)
async def get_component_by_id_with_descendants(project_id: int, component_id: int, db: AsyncSession = Depends(get_db)) -> ComponentWithDescendants:
    try:
        component = await get_component_hierarchy(component_id, db=db, levels=1)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@ router.get("/{component_slug:str}/with-descendants", response_model=ComponentWithDescendants)
async def get_component_by_slug_with_descendants(project_id: int, component_slug: str, db: AsyncSession = Depends(get_db)) -> ComponentWithDescendants:
    try:
        component_id = await SqlComponent.get_id_by_slug(db, project_id, component_slug)
        component = await SqlComponent.get_with_descendants_by_slug(db, project_id, component_id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@ router.put("/{component_id:int}", response_model=Component)
async def update_component_by_id(project_id: int, component_id: int, component: ComponentUpdate, db: AsyncSession = Depends(get_db)) -> Component:
    # Component ID is unique across all projects, so project_slug is irrelavant
    try:
        sql_component_to_update = await SqlComponent.get_by_id(db, component_id)
        if sql_component_to_update is None:
            raise ValueError(
                f"Component does not exist")
        model_to_update = Component.model_validate(sql_component_to_update)
        dict_to_update = model_to_update.model_dump()
        for key, value in component.model_dump().items():
            if value is not None:
                dict_to_update[key] = value
        updated_component = ComponentUpdate(**dict_to_update)
        with ensure_request_validation_errors("body"):
            await updated_component.model_async_validate()
        component = await SqlComponent.update(db, component_id, **updated_component.model_dump())
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return component


@ router.put("/{component_slug:str}", response_model=Component)
async def update_component_by_slug(project_id: int, component_slug: str, component: ComponentUpdate, db: AsyncSession = Depends(get_db)) -> Component:
    # Component ID is unique across all projects, so project_slug is irrelavant
    component_id = await SqlComponent.get_id_by_slug(db, project_id, component_slug)
    try:
        with ensure_request_validation_errors("body"):
            await component.model_async_validate()
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
            "slug": component.slug,
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
