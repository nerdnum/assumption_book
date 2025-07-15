# Standard libary imports
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.pydantic_models.project_model import (
    DocResponse,
    DocSpec,
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectWithProjectRoles,
)

# App imports
from app.pydantic_models.role_model import Role
from app.pydantic_models.project_model import Project
from app.services.create_docx import create_project_docx, create_project_xlsx
from app.services.database import get_db
from app.sqlalchemy_models.user_project_role_sql import (
    Project as SqlProject,
    User as SqlUser,
    UserProject as SqlUserProject,
    UserProjectRole as SqlUserProjectRole,
)
from app.views.auth_view import get_current_user_with_roles
from app.views.users_view import construct_user

# App imports

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/user-projects", response_model=list[ProjectWithProjectRoles])
async def get_current_user_projects(
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    """Gets the list of project that a user can access with the roles assigned to that user."""
    user = await construct_user(db, current_user.id)
    return user["projects"]


@router.get("", response_model=list[ProjectWithProjectRoles])
async def get_all_projects(
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    """Provides a list of all projects in the system."""
    projects = await SqlProject.get_all(db)
    return projects


@router.post("", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    """Creates a new project in the system."""
    try:
        project = await SqlProject.create(
            db, user_id=current_user.id, **project.model_dump()
        )
        await db.commit()
        await db.refresh(project)
        association = SqlUserProject(
            user_id=current_user.id,
            project_id=project.id,
            created_by=current_user.id,
            updated_by=current_user.id,
        )
        db.add(association)
        await db.commit()
        await db.refresh(association)
        await db.refresh(project)

    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return project


## These functions were implement using websockets
# @router.get("/docx", response_model=DocResponse)
# async def get_project_document_by_id(
#     spec: DocSpec,
#     db: AsyncSession = Depends(get_db),
#     current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
# ) -> str:
#     document_path = await create_project_docx(spec)
#     return document_path


# @router.get("/xlsx", response_model=DocResponse)
# async def get_project_document_by_id(
#     spec: DocSpec,
#     db: AsyncSession = Depends(get_db),
#     current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
# ) -> str:
#     document_path = await create_project_xlsx(spec)
#     return document_path


@router.get("/{id:int}", response_model=Project)
async def get_project_by_param_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> Project:
    """Gets a project by its ID."""
    try:
        project = await SqlProject.get_project_by_id(db, id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return project


@router.get("/{id:int}/roles", response_model=ProjectWithProjectRoles)
async def get_project_roles(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> Project:
    """Gets a project by its ID along with the roles associated with it."""
    try:
        project = await SqlProject.get_project_by_id(db, id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return project


# @router.get("/{id:int}/users", response_model=ProjectWithUsers)
# async def get_project_users(
#     id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
# ) -> ProjectWithUsers:
#     """Gets a project by its ID along with the users that can access it."""
#     try:
#         project = await SqlProject.get_project_by_id(db, id)
#     except ValueError as error:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
#     return project


@router.put(
    "/{id:int}",
    response_model=Project,
)
async def update_project_by_id(
    id: int,
    project: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> Project:
    """Updates the basic data of a project by its ID."""
    try:
        project = await SqlProject.update_by_id(
            db,
            user_id=current_user.id,
            id=id,
            **project.model_dump(),
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return project


@router.post(
    "/{id:int}/roles/{role_id:int}",
    response_model=ProjectWithProjectRoles,
)
async def add_project_role(
    id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> Project:
    """Add a new user role to a project."""
    try:
        project = await SqlProject.add_project_role(
            db, user_id=current_user.id, project_id=id, project_role_id=role_id
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return project


@router.delete("/{id:int}", response_model=Project)
async def delete_project_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> Project:
    """Deletes a project by its ID."""
    try:
        project = await SqlProject.delete_by_id(db, id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return project


# @router.get("/project-role/{id:int}", response_model=dict)
# async def get_project_role_by_id(
#     id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
# ) -> dict:
#     try:
#         project_role = await SqlUserProjectRole.get(db, id)
#     except ValueError as error:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
#     return {
#         "id": project_role.id,
#         "project_id": project_role.project_id,
#         "role_id": project_role.role_id,
#     }


@router.get("/framework", response_model=None)
def get_framework(
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    return [
        {
            "sequence": 1,
            "title": "Introduction",
            "defaultText": "This is an introduction",
            "context": "information",
        },
        {
            "sequence": 2,
            "defaultText": "This is the default text",
            "title": "Directives",
            "context": "decisions",
        },
        {
            "sequence": 3,
            "defaultText": "This is the default text",
            "title": "Givens",
            "context": "decisions",
        },
        {
            "sequence": 4,
            "defaultText": "This is the default text",
            "title": "Assumptions",
            "context": "decisions",
        },
        {
            "defaultText": "This is the default text",
            "title": "Key Decisions",
            "context": "decisions",
        },
        {
            "sequence": 6,
            "defaultText": "This is the default text",
            "title": "Studies",
            "context": "studies",
        },
        {
            "sequence": 7,
            "defaultText": "This is the default text",
            "title": "Standards",
            "context": "studies",
        },
        {
            "sequence": 8,
            "defaultText": "This is the default text",
            "title": "Boundaries",
            "context": "parameters",
        },
        {
            "sequence": 9,
            "defaultText": "This is the default text",
            "title": "Interface",
            "context": "interface",
        },
        {
            "sequence": 10,
            "defaultText": "This is the default text",
            "title": "Parameters",
            "context": "parameters",
        },
        {
            "sequence": 11,
            "defaultText": "This is the default text",
            "title": "Location",
            "context": "parameters",
        },
        {
            "sequence": 12,
            "defaultText": "This is the default text",
            "title": "Environmental & Social",
            "context": "studies",
        },
        {
            "sequence": 13,
            "defaultText": "This is the default text",
            "title": "Health and Safety",
            "context": "studies",
        },
        {
            "sequence": 14,
            "defaultText": "This is the default text",
            "title": "Waste Management",
            "context": "information",
        },
        {
            "sequence": 15,
            "defaultText": "This is the default text",
            "title": "Consultants",
            "context": "parameters",
        },
    ]
