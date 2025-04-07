# Standard libary imports
from typing import Any, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.pydantic_models.role_model import Role, RoleCreate, RoleUpdate

# RoleWithUsers
# App imports
from app.services.database import get_db
from app.sqlalchemy_models.user_project_role_sql import User as SqlUser
from app.sqlalchemy_models.user_project_role_sql import Role as SqlRole
from app.views.auth_view import get_current_user_with_roles

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=list[Role])
async def get_all_roles(
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    roles = await SqlRole.get_all(db)
    return roles


@router.post("", response_model=Role, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        role_in_db = await SqlRole.create(
            db, role.name, role.description, role.is_system_role
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return role_in_db


@router.put("/{id}", response_model=Role)
async def update_role(
    id: int,
    role: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        role_in_db = await SqlRole.update(
            db, id, role.name, role.description, role.is_system_role
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return role_in_db


@router.delete("/{id}", response_model=Any)
async def delete_role(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        await SqlRole.delete(db, id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return {"detail": "Role deleted"}


@router.get("/{id}", response_model=Role)
async def get_role_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        role = await SqlRole.get(db, id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return role


@router.get("/uuid/{uuid}", response_model=Role)
async def get_role_by_uuid(
    uuid: str,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        role = await SqlRole.get_role_by_uuid(db, uuid)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return role


# @router.post(
#     "/{role_id}/user/{user_id}",
#     response_model=RoleWithUsers,
#     status_code=status.HTTP_201_CREATED,
# )
# async def add_user_to_role(
#     user_id: int, role_id: int, db: AsyncSession = Depends(get_db)
# ):
#     try:
#         await SqlUser.add_role(db, user_id, role_id)
#         role = await SqlRole.get(db, role_id)
#     except ValueError as error:
#         raise HTTPException(status_code=400, detail=str(error))
#     return role


# @router.get("/{role_id}/users", response_model=RoleWithUsers)
# async def get_users_in_role(role_id: int, db: AsyncSession = Depends(get_db)):
#     try:
#         role = await SqlRole.get(db, role_id)
#     except ValueError as error:
#         raise HTTPException(status_code=404, detail=str(error))
#     return role


@router.delete("/{role_id}/user/{user_id}", response_model=Any)
async def remove_user_from_role(
    user_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        await SqlRole.remove_user_from_role(db, user_id, role_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return {"detail": "User removed from role"}
