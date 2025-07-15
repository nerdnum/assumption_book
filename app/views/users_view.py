from typing import Annotated, Any, List, Sequence
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, select
from rich import print

from app.config import get_config
from app.pydantic_models.user_model import (
    User,
    UserCreate,
    UserUpdate,
    ProjectWithProjectRoles,
    UserWithProjectRoles,
    UserWithProjectsAndSystemRoles,
)
from app.pydantic_models.project_model import (
    ProjectBasicInfo,
    RoleRequest,
    Project,
    ProjectWithProjectRoles,
)
from app.services.database import get_db


from app.sqlalchemy_models.user_project_role_sql import (
    User as SqlUser,
    Project as SqlProject,
    ProjectRole as SqlProjectRole,
    UserProject as SqlUserProject,
    UserProjectRole as SqlUserProjectRole,
    UserSystemRole as SqlUserSystemRole,
    Role as SqlRole,
)

from app.views.auth_view import get_current_user, get_current_user_with_roles
from app.services.security import Authorizations

config = get_config()
router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[],
)


async def get_user_project_role_ids(db, project_id: int, user_id: int) -> List[int]:
    user_project_roles = (
        (
            await db.execute(
                select(
                    SqlUserProjectRole.project_role_id.label("user_project_role_id"),
                    SqlProjectRole.project_id,
                    SqlProjectRole.role_id,
                )
                .join(
                    SqlProjectRole,
                    SqlUserProjectRole.project_role_id == SqlProjectRole.id,
                )
                .where(
                    SqlUserProjectRole.user_id == user_id,
                    SqlProjectRole.project_id == project_id,
                )
            )
        )
        .mappings()
        .all()
    )
    records = [role["role_id"] for role in user_project_roles]
    return records


async def construct_user(db, user_id: int):
    """Helper function to get a user by ID."""
    # user = await SqlUser.get(db, user_id)
    user = (
        (
            await db.execute(
                select(SqlUser)
                .filter(SqlUser.id == user_id)
                .options(
                    selectinload(SqlUser.projects),
                    selectinload(SqlUser.project_roles),
                    selectinload(SqlUser.system_roles),
                )
            )
        )
        .scalars()
        .first()
    )
    # from_attributes=True is needed to allow the model to be created from the SQLAlchemy model
    # and follow all the attributes recursively, other wise it only validates the top level attributes
    # and gives an error for the nested attribute
    pydantic_user = UserWithProjectsAndSystemRoles.model_validate(
        user, from_attributes=True
    )

    user_dict = pydantic_user.model_dump()
    user_projects = user_dict.get("projects", [])
    for project in user_projects:
        user_role_ids = await get_user_project_role_ids(
            db, project_id=project["id"], user_id=user_id
        )
        project["project_roles"] = [
            role for role in project["project_roles"] if role["id"] in user_role_ids
        ]

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_dict


@router.get("", response_model=Sequence[UserWithProjectsAndSystemRoles])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    """Get all users in the system."""
    users = await SqlUser.get_all(db)
    users_to_return = []
    for user in users:
        users_to_return.append(await construct_user(db, user.id))
    return users_to_return


@router.post(
    "",
    response_model=UserWithProjectsAndSystemRoles,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    """Add a new user to the system."""
    try:
        user = await SqlUser.create(
            db,
            user_id=current_user.id,
            full_name=user.full_name,
            preferred_name=user.preferred_name or None,
            email=user.email.lower(),
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return await construct_user(db, user.id)


@router.put("/{id}/activate", response_model=None)
async def do_activation(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):
    try:
        await SqlUser.activate(db, current_user.id, id)
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
        await SqlUser.deactivate(db, current_user.id, id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return {"detail": "User deactivated"}


@router.get("/{id:int}", response_model=UserWithProjectsAndSystemRoles)
async def get_user(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        user = await construct_user(db, id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return await construct_user(db, user.id)


@router.put("/{id}", response_model=UserWithProjectsAndSystemRoles)
async def update_user(
    id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):
    try:
        user = await SqlUser.update(
            db,
            current_user.id,
            id,
            user.full_name,
            None,
            user.preferred_name,
            user.email.lower() if user.email else None,
            user.is_active,
            user.is_superuser,
            user.system_roles,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return await construct_user(db, user.id)


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


@router.get("/{id}/projects", response_model=List[ProjectWithProjectRoles])
async def get_user_projects(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        user = await construct_user(db, id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return user["projects"]


@router.post("/{id}/projects", response_model=List[ProjectWithProjectRoles])
async def set_user_projects(
    id: int,
    project_ids: List[int],
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):
    """Set projects for user according to the list of project IDs."""

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
                uuid=str(uuid.uuid4()),
                created_by=current_user.id,
                updated_by=current_user.id,
            )
            db.add(association)
            await db.commit()
            await db.refresh(user)
        await db.flush()
        user_for_return = await construct_user(db, id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    user = await construct_user(db, id)
    return user_for_return["projects"]


# Not require for this project, but can be uncommented if needed
#
# @router.get("/username/{username}", response_model=User)
# async def get_user_by_username(
#     username: str,
#     db: AsyncSession = Depends(get_db),
#     current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
# ):
#     try:
#         user = await SqlUser.get_user_by_username(db, username)
#     except ValueError as error:
#         raise HTTPException(status_code=400, detail=str(error))
#     return user


@router.get("/uuid/{uuid}", response_model=User)
async def get_user_by_uuid(
    uuid: str,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        user = await SqlUser.get_user_by_uuid(db, uuid)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return await construct_user(db, user.id)


async def do_project_role_checks(project_id: int, role_id: int, db: AsyncSession):
    """Helper function to check if the project role exists and is valid."""
    project = (
        await db.execute(
            select(SqlProject)
            .where(SqlProject.id == project_id)
            .options(
                selectinload(SqlProject.project_roles),
            )
        )
    ).scalar_one_or_none()
    if project is None:
        raise ValueError("Project not found")

    role = await SqlRole.get(db, role_id)
    if role is None:
        raise ValueError("Role not found")

    if role.is_system_role:
        raise ValueError("Cannot associate a system role with a project.")

    if role not in project.project_roles:
        raise ValueError("The role is not associated with the project")

    return project, role


async def set_user_project_role(
    user_id: int, project_id: int, role_id: int, db: AsyncSession, current_user: SqlUser
):
    """Helper function to set a user project role."""
    user = await SqlUser.get(db, user_id)
    if user is None:
        raise ValueError("User not found")

    project, role = await do_project_role_checks(project_id, role_id, db)

    project_role = (
        await db.execute(
            select(SqlProjectRole).where(
                SqlProjectRole.project_id == project.id,
                SqlProjectRole.role_id == role.id,
            )
        )
    ).scalar_one()

    user_project_role = (
        await db.execute(
            select(SqlUserProjectRole).where(
                SqlUserProjectRole.user_id == user.id,
                SqlUserProjectRole.project_role_id == project_role.id,
            )
        )
    ).scalar_one_or_none()

    if user_project_role is not None:
        raise ValueError("User already has this project role")

    new_user_project_role = SqlUserProjectRole(
        user_id=user.id,
        project_role_id=project_role.id,
        uuid=str(uuid.uuid4()),
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    db.add(new_user_project_role)
    await db.commit()
    await db.refresh(user)
    return new_user_project_role


async def do_user_project_role_checks(
    user_id: int, project_id: int, role_id: int, db: AsyncSession
):
    """Helper function to check if the user has access to the project."""

    project_role = (
        await db.execute(
            select(SqlProjectRole).where(
                SqlProjectRole.project_id == project_id,
                SqlProjectRole.role_id == role_id,
            )
        )
    ).scalar_one()
    if project_role is None:
        raise ValueError("Project role not found")

    user_project_role = (
        await db.execute(
            select(SqlUserProjectRole).where(
                SqlUserProjectRole.user_id == user_id,
                SqlUserProjectRole.project_role_id == project_role.id,
            )
        )
    ).scalar_one_or_none()

    return project_role, user_project_role


async def remove_user_project_role(
    user_id: int,
    project_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        """Helper function to remove a project role for a user."""
        project, role = await do_project_role_checks(project_id, role_id, db)

        project_role, user_project_role = await do_user_project_role_checks(
            user_id=user_id,
            project_id=project_id,
            role_id=role_id,
            db=db,
        )

        if user_project_role is None:
            raise ValueError("User project role does not exist")

        await db.delete(user_project_role)
        await db.commit()
        return user_project_role
    except Exception:
        raise


@router.post(
    "/{user_id:int}/project-role",
    response_model=UserWithProjectsAndSystemRoles,
    status_code=status.HTTP_201_CREATED,
)
async def add_project_role_for_user(
    user_id: int,
    role_request: RoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        user = await SqlUser.get(db, user_id)
        if user is None:
            raise ValueError("User not found")

        await do_project_role_checks(role_request.project_id, role_request.role_id, db)

        await set_user_project_role(
            user_id=user.id,
            project_id=role_request.project_id,
            role_id=role_request.role_id,
            db=db,
            current_user=current_user,
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return await construct_user(db, user_id)


@router.delete(
    "/{user_id:int}/project-role",
    response_model=UserWithProjectsAndSystemRoles,
)
async def remove_project_role_for_user_request(
    user_id: int,
    role_request: RoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):
    try:

        project, role = await do_project_role_checks(
            role_request.project_id, role_request.role_id, db
        )

        user_project_role = await remove_user_project_role(
            user_id=user_id,
            project_id=role_request.project_id,
            role_id=role_request.role_id,
            db=db,
        )
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    return await construct_user(db, user_id)


@router.post(
    "/{user_id:int}/project-roles",
    response_model=List[ProjectWithProjectRoles],
)
async def set_project_roles_for_user(
    user_id: int,
    roles_config: List[ProjectWithProjectRoles],
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):
    try:
        # First check everything before try to make any changes to the user

        user = await SqlUser.get(db, user_id)

        if user is None:
            raise ValueError("User not found")

        desired_user_project_ids = []
        for project in roles_config:
            try:
                project_db = await SqlProject.get_project_by_id(db, project.id)
                if project_db is None:
                    raise ValueError(f"Project with ID {project.id} not found")
                desired_user_project_ids.append(project_db.id)
                # Will raise a ValueError if the role is not valid for the project
                for role in project.project_roles:
                    _, project_role = await do_project_role_checks(
                        project.id, role.id, db
                    )
            except ValueError:
                raise

        updated_projects = await set_user_projects(
            user_id, desired_user_project_ids, db, current_user
        )

        # TODO: clean up user project roles

        user_project_roles = {}
        for project in updated_projects:
            user_project_roles[project["id"]] = [
                role["id"] for role in project["project_roles"]
            ]

        request_dict = {}
        for project in roles_config:
            request_dict[project.id] = [role.id for role in project.project_roles]

        set_requests = []
        remove_requests = []

        for project_id, role_ids in request_dict.items():
            current_role_ids = user_project_roles.get(project_id, [])
            for role_id in role_ids:
                if role_id not in current_role_ids:
                    set_requests.append((user_id, project_id, role_id))
            for role_id in current_role_ids:
                if role_id not in role_ids:
                    remove_requests.append((user_id, project_id, role_id))

        # for project_id, role_ids in add_project_with_roles.items():

        for user_id, project_id, role_id in set_requests:
            await set_user_project_role(
                user_id=user_id,
                project_id=project_id,
                role_id=role_id,
                db=db,
                current_user=current_user,
            )
        for user_id, project_id, role_id in remove_requests:
            await remove_user_project_role(
                user_id=user_id, project_id=project_id, role_id=role_id, db=db
            )
    except Exception as error:
        raise  # HTTPException(status_code=404, detail=str(error))

    user_to_return = await construct_user(db, user_id)
    return user_to_return["projects"]


@router.post(
    "/{user_id:int}/system-role/{role_id:int}",
    response_model=UserWithProjectsAndSystemRoles,
    status_code=status.HTTP_201_CREATED,
)
async def add_system_role_for_user(
    user_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):

    try:
        user = await SqlUser.get(db, user_id)
        if user is None:
            raise ValueError("User not found")
        role = await SqlRole.get(db, role_id)
        if role is None:
            raise ValueError("Role not found")
        if not role.is_system_role:
            raise ValueError("The role is not a system role")
        user_system_role = await SqlUserSystemRole.create(
            db, current_user.id, user_id_for_role=user_id, system_role_id=role_id
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return await construct_user(db, user_id)


@router.delete(
    "/{user_id:int}/system-role/{role_id:int}",
    response_model=UserWithProjectsAndSystemRoles,
    status_code=status.HTTP_201_CREATED,
)
async def remove_system_role_for_user(
    user_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):
    try:
        system_role = await SqlUserSystemRole.get(db, user_id, role_id)
        if system_role is None:
            raise ValueError("System role not found for this user")
        await db.delete(system_role)
        await db.commit()
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return await construct_user(db, user_id)


# @router.get("/{id}/roles", response_model=UserWithProjectRoles)
# async def get_user_with_project_and_roles_for_projects(
#     id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
# ):
#     try:
#         user = await SqlUser.get(db, id)
#         if not user:
#             raise ValueError("User not found")
#         # if len(user.projects) == 0:
#         #     raise ValueError("This user has not been assigned any projects")
#         # users_roles = await SqlUserProjectRoles.get_user_roles_accross_all_projects(
#         #     db, id
#         # )
#         # user_role_ids = [role.id for role in users_roles]
#         # if not users_roles:
#         #     raise ValueError("This user has not been assigned any roles")
#         # for project in user.projects:
#         #     for index in range(len(project.roles) - 1, -1, -1):
#         #         if not project.roles[index].id in user_role_ids:
#         #             del project.roles[index]
#     except ValueError as error:
#         raise HTTPException(status_code=400, detail=str(error))
#     return user


@router.get(
    "/{id}/project-authorizations", response_model=Sequence[ProjectWithProjectRoles]
)
async def get_user_authorisation(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        user = await SqlUser.get(db, id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return user.projects


# @router.delete("/{user_id}/role/{role_id}", response_model=Any)
# async def remove_role_for_user(
#     user_id: int,
#     role_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
# ):
#     try:
#         user = await SqlRole.remove_user_from_role(db, user_id, role_id)
#     except ValueError as error:
#         raise HTTPException(status_code=400, detail=str(error))
#     return user
