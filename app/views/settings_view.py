from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.pydantic_models.setting_model import Setting, SettingCreate, SettingUpdate
from app.services.database import get_db
from app.sqlalchemy_models.settings_sql import Setting as SqlSetting
from app.sqlalchemy_models.user_project_role_sql import User as SqlUser
from app.views.auth_view import get_current_user_with_roles


router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=list[Setting])
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    settings = await SqlSetting.get_all(db)
    return settings


# const settingToSave = {
#       id: setting.id,
#       settingTypeId: setting.settingTypeId,
#       title: setting.title,
#       description: setting.title,
#       value: setting.value,
#     };


@router.post("", response_model=Setting, status_code=status.HTTP_201_CREATED)
async def create_setting(
    setting: SettingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        setting = await SqlSetting.create(
            db, user_id=current_user.id, **setting.model_dump()
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return setting


@router.get("/{id}", response_model=Setting)
async def get_setting(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        setting = await SqlSetting.get(db, id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return setting


@router.put("/{id}", response_model=Setting)
async def update_setting(
    id: int,
    setting: SettingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        setting = await SqlSetting.update(
            db, user_id=current_user.id, id=id, **setting.model_dump()
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return setting


@router.delete("/{id}", response_model=None)
async def delete_setting(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        result = await SqlSetting.delete(db, id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return result
