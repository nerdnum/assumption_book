from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.pydantic_models.setting_model import Setting, SettingCreate, SettingUpdate
from app.services.database import get_db
from app.sqlalchemy_models.settings_sql import Setting as SqlSetting

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=list[Setting])
async def get_settings(db: AsyncSession = Depends(get_db)):
    settings = await SqlSetting.get_all(db)
    return settings


@router.post("", response_model=Setting, status_code=status.HTTP_201_CREATED)
async def create_setting(setting: SettingCreate, db: AsyncSession = Depends(get_db)):
    try:
        setting = await SqlSetting.create(db, **setting.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return setting


@router.get("/{id}", response_model=Setting)
async def get_setting(id: int, db: AsyncSession = Depends(get_db)):
    try:
        setting = await SqlSetting.get(db, id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return setting


@router.put("/{id}", response_model=Setting)
async def update_setting(
    id: int, setting: SettingUpdate, db: AsyncSession = Depends(get_db)
):
    try:
        setting = await SqlSetting.update(db, id, **setting.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return setting


@router.delete("/{id}", response_model=None)
async def delete_setting(id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await SqlSetting.delete(db, id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return result
