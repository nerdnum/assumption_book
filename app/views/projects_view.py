# Standard libary imports
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.pydantic_models.project_model import Project, ProjectCreate, ProjectUpdate

# App imports
from app.services.database import get_db
from app.sqlalchemy_models.projects_sql import Project as SqlProject

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[Project])
async def get_all_projects(db: AsyncSession = Depends(get_db)):
    projects = await SqlProject.get_all(db)
    return projects


@router.post("", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_db)):
    try:
        project = await SqlProject.create(db, **project.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return project


@router.get("/framework", response_model=None)
def get_framework():
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
            "title": "Interfaces",
            "context": "parameters",
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


@router.get("/{id:int}", response_model=Project)
async def get_project_by_id(id: int, db: AsyncSession = Depends(get_db)) -> Project:
    try:
        project = await SqlProject.get_by_id(db, id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return project


@router.put("/{id:int}", response_model=Project)
async def update_project_by_id(
    id: int, project: ProjectUpdate, db: AsyncSession = Depends(get_db)
) -> Project:
    try:
        project = await SqlProject.update_by_id(db, id, **project.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return project


@router.delete("/{id:int}", response_model=Project)
async def delete_project_by_id(id: int, db: AsyncSession = Depends(get_db)) -> Project:
    try:
        result = await SqlProject.delete_by_id(db, id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return result
