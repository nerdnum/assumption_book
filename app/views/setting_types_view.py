from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.pydantic_models.setting_type_model import (
    SettingType,
    SettingTypeCreate,
    SettingTypeUpdate,
)
from app.services.database import get_db
from app.sqlalchemy_models.setting_types_sql import SettingType as SqlSettingType
from app.sqlalchemy_models.user_project_role_sql import User as SqlUser
from app.views.auth_view import get_current_user_with_roles

router = APIRouter(prefix="/setting-types", tags=["setting-types"])


@router.get("", response_model=list[SettingType])
async def get_setting_types(db: AsyncSession = Depends(get_db)):
    setting_types = await SqlSettingType.get_all(db)
    return setting_types


@router.post("", response_model=SettingType, status_code=status.HTTP_201_CREATED)
async def create_setting_type(
    setting_type: SettingTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        setting_type = await SqlSettingType.create(
            db, **setting_type.model_dump(), user_id=current_user.id
        )
    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return setting_type


@router.get("/{id}", response_model=SettingType)
async def get_setting(id: int, db: AsyncSession = Depends(get_db)):
    try:
        setting = await SqlSettingType.get(db, id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return setting


@router.put("/{id}", response_model=SettingType)
async def update_setting(
    id: int, setting_type: SettingTypeUpdate, db: AsyncSession = Depends(get_db)
):
    try:
        setting_type = await SqlSettingType.update(db, id, **setting_type.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return setting_type


@router.delete("/{id}", response_model=None)
async def delete_setting(id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await SqlSettingType.delete(db, id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return result
