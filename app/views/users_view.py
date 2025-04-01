from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select

from app.config import get_config
from app.pydantic_models.user_model import (
    User,
    UserCreate,
    UserUpdate,
    UserWithProjects,
    UserWithProjectRoles,
)
from app.pydantic_models.project_model import ProjectBasicInfo
from app.services.database import get_db
from app.sqlalchemy_models.user_project_role_sql import Role as SqlRole
from app.sqlalchemy_models.user_project_role_sql import User as SqlUser
from app.sqlalchemy_models.user_project_role_sql import UserRole as SqlUserRole
from app.sqlalchemy_models.user_project_role_sql import Project as SqlProject
from app.sqlalchemy_models.user_project_role_sql import UserProject as SqlUserProject

from app.views.auth_view import get_current_user, get_current_user_with_roles
from app.services.security import Authorizations

config = get_config()
router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[],
)


@router.get("", response_model=list[UserWithProjects])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    users = await SqlUser.get_all(db)
    return users


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        user = await SqlUser.create(
            db, user.username, user.full_name, user.email, current_user.id
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return user


@router.put("/{id}/activate", response_model=None)
async def do_activation(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):
    try:
        await SqlUser.activate(db, id, current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return {"detail": "User activated"}


@router.put("/{id}/deactivate", response_model=None)
async def do_deactivation(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):
    try:
        await SqlUser.deactivate(db, id, current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return {"detail": "User deactivated"}


@router.get("/{id}", response_model=UserWithProjects)
async def get_user(id: int, db: AsyncSession = Depends(get_db)):
    try:
        user = await SqlUser.get(db, id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return user


@router.get("/{id}/authorizations", response_model=UserWithProjectRoles)
async def get_user_authorisation(id: int, db: AsyncSession = Depends(get_db)):
    try:
        user = await SqlUser.get_user_project_roles(db, id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return user


@router.put("/{id}", response_model=User)
async def update_user(
    id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):
    try:
        user = await SqlUser.update(
            db,
            id,
            user.full_name,
            user.username,
            user.preferred_name,
            user.email,
            user.is_active,
            user.is_superuser,
            current_user.id,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return user


@router.delete("/{id}", response_model=None)
async def delete_user(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):
    try:
        result = await SqlUser.delete(db, id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return result


@router.get("/{id}/projects", response_model=List[ProjectBasicInfo])
async def get_user_projects(id: int, db: AsyncSession = Depends(get_db)):
    try:
        user = await SqlUser.get(db, id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return user.projects


@router.post("/{id}/projects", response_model=UserWithProjects)
async def set_user_projects(
    id: int,
    project_ids: List[int],
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):
    try:
        user = await SqlUser.get(db, id)
        projects_to_remove = []
        for project in user.projects:
            if project.id not in project_ids:
                projects_to_remove.append(project.id)
            else:
                project_ids.remove(project.id)
        associations = (
            await db.execute(
                select(SqlUserProject).filter(
                    and_(
                        SqlUserProject.user_id == user.id,
                        SqlUserProject.project_id.in_(projects_to_remove),
                    )
                )
            )
        ).all()
        for association in associations:
            await db.delete(association[0])
        await db.commit()
        await db.refresh(user)
        for project_id in project_ids:
            association = SqlUserProject(
                user_id=user.id,
                project_id=project_id,
                created_by=current_user.id,
                updated_by=current_user.id,
            )
            db.add(association)
            await db.commit()
            await db.refresh(user)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return user


@router.get("/username/{username}", response_model=User)
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    try:
        user = await SqlUser.get_user_by_username(db, username)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return user


@router.get("/uuid/{uuid}", response_model=User)
async def get_user_by_uuid(uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        user = await SqlUser.get_user_by_uuid(db, uuid)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return user


@router.post(
    "/{user_id}/role",
    response_model=UserWithProjectRoles,
    status_code=status.HTTP_201_CREATED,
)
async def add_role_for_user(
    user_id: int,
    role_id: int,
    project_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):
    try:
        await SqlUserRole.create(db, user_id, role_id, project_id, current_user.id)
        user = await SqlUser.get_user_project_roles(db, user_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return user


@router.get("/{id}/roles", response_model=UserWithProjectRoles)
async def get_user_with_roles(id: int, db: AsyncSession = Depends(get_db)):
    try:
        user = await SqlUser.get(db, id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return user


@router.delete("/{user_id}/role/{role_id}", response_model=Any)
async def remove_role_for_user(
    user_id: int, role_id: int, db: AsyncSession = Depends(get_db)
):
    try:
        user = await SqlRole.remove_user_from_role(db, user_id, role_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return user
