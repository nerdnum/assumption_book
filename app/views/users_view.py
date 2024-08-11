from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.config import get_config
from app.services.database import get_db
from app.pydantic_models.user_model import User, UserCreate, UserUpdate, UserWithRoles
from app.sqlalchemy_models.users_sql import User as SqlUser, Role as SqlRole
from typing import Any


config = get_config()
router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[User])
async def get_users(db: AsyncSession = Depends(get_db)):
    users = await SqlUser.get_all(db)
    return users


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await SqlUser.create(db, user.username, user.full_name, user.email)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return user


@router.get("/{id}", response_model=User)
async def get_user(id: int, db: AsyncSession = Depends(get_db)):
    try:
        user = await SqlUser.get(db, id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{id}", response_model=User)
async def update_user(id: int, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    try:
        user = await SqlUser.update(db, id, user.username, user.full_name, user.email)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return user


@router.delete("/{id}", response_model=None)
async def delete_user(id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await SqlUser.delete(db, id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return result


@router.get("/username/{username}", response_model=User)
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    try:
        user = await SqlUser.get_user_by_username(db, username)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return user


@router.get("/uuid/{uuid}", response_model=User)
async def get_user_by_uuid(uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        user = await SqlUser.get_user_by_uuid(db, uuid)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return user


@router.post("/{user_id}/role/{role_id}", response_model=UserWithRoles, status_code=status.HTTP_201_CREATED)
async def add_role_for_user(user_id: int, role_id: int, db: AsyncSession = Depends(get_db)):
    try:
        user = await SqlUser.add_role(db, user_id, role_id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return user


@router.get("/{id}/roles", response_model=UserWithRoles)
async def get_user_with_roles(id: int, db: AsyncSession = Depends(get_db)):
    try:
        user = await SqlUser.get(db, id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return user


@router.delete("/{user_id}/role/{role_id}", response_model=Any)
async def remove_role_for_user(user_id: int, role_id: int, db: AsyncSession = Depends(get_db)):
    try:
        user = await SqlRole.remove_user_from_role(db, user_id, role_id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return user


@router.put("/activate/{id}", response_model=None)
async def do_activation(id: int, db: AsyncSession = Depends(get_db)):
    if config['config_name'] != 'testing':
        raise HTTPException(
            status_code=404, detail="Not found")
    try:
        user = await SqlUser.activate(db, id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return {"detail": "User activated"}


@router.put("/deactivate/{id}", response_model=None)
async def do_deactivation(id: int, db: AsyncSession = Depends(get_db)):
    if config['config_name'] != 'testing':
        raise HTTPException(
            status_code=404, detail="Not found")
    try:
        user = await SqlUser.deactivate(db, id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return {"detail": "User deactivated"}
