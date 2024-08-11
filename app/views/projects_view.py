# Standard libary imports
from app.views.components_view_project_id import router as id_component_router
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
from slugify import slugify

# App imports
from app.services.database import get_db
from app.sqlalchemy_models.projects_sql import Project as SqlProject
from app.pydantic_models.project_model import ProjectCreate, ProjectUpdate, Project


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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return project


@router.post("/{slug:str}", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(slug: str, project: ProjectCreate, db: AsyncSession = Depends(get_db)):
    try:
        assert slug == slugify(slug), "Slug is not valid"
        project.slug = slug
        project = await SqlProject.create(db, **project.model_dump())
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    except AssertionError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return project


@router.get('/framework', response_model=None)
def get_framework():
    return [
        {
            "id": 1,
            "sequence": 1,
            "title": "Introduction",
            "default_text": "This is an introduction"
        },
        {"id": 2, "sequence": 2, "default_text": "This is the default text",
            "title": "Directives"},
        {"id": 3, "sequence": 3,
            "default_text": "This is the default text", "title": "Givens"},
        {"id": 4, "sequence": 4, "default_text": "This is the default text",
            "title": "Assumptions"},
        {"id": 5, "sequence": 5, "default_text": "This is the default text",
            "title": "Key Decisions"},
        {"id": 6, "sequence": 6,
            "default_text": "This is the default text", "title": "Studies"},
        {"id": 7, "sequence": 7, "default_text": "This is the default text",
            "title": "Standards"},
        {"id": 8, "sequence": 8, "default_text": "This is the default text",
            "title": "Boundaries"},
        {"id": 9, "sequence": 9, "default_text": "This is the default text",
            "title": "Interfaces"},
        {"id": 10, "sequence": 10, "default_text": "This is the default text",
            "title": "Parameters"},
        {"id": 11, "sequence": 11, "default_text": "This is the default text",
            "title": "Location"},
        {"id": 12, "sequence": 12, "default_text": "This is the default text",
            "title": "Environmental & Social"},
        {"id": 13, "sequence": 13, "default_text": "This is the default text",
            "title": "Health and Safety"},
        {"id": 14, "sequence": 14, "default_text": "This is the default text",
            "title": "Waste Managements"},
        {"id": 15, "sequence": 15, "default_text": "This is the default text",
            "title": "Consultants"}
    ]


@router.get("/{id:int}", response_model=Project)
async def get_project_by_id(id: int, db: AsyncSession = Depends(get_db)) -> Project:
    try:
        project = await SqlProject.get_by_id(db, id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return project


@router.get("/{slug:str}", response_model=Project)
async def get_project_by_slug(slug: str, db: AsyncSession = Depends(get_db)) -> Project:
    try:
        project = await SqlProject.get_by_slug(db, slug)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return project


@ router.put("/{id:int}", response_model=Project)
async def update_project_by_id(id: int, project: ProjectUpdate, db: AsyncSession = Depends(get_db)) -> Project:
    try:
        project = await SqlProject.update_by_id(db, id, **project.model_dump())
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return project


@ router.put("/{slug:str}", response_model=Project)
async def update_project_by_slug(slug: str, project: ProjectUpdate, db: AsyncSession = Depends(get_db)) -> Project:
    try:
        project = await SqlProject.update_by_slug(db, lookup_slug=slug, **project.model_dump())
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return project


@ router.delete("/{id:int}", response_model=Project)
async def delete_project_by_id(id: int, db: AsyncSession = Depends(get_db)) -> Project:
    try:
        result = await SqlProject.delete_by_id(db, id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return result


@ router.delete("/{slug:str}", response_model=Project)
async def delete_project_by_slug(slug: str, db: AsyncSession = Depends(get_db)) -> Project:
    try:
        result = await SqlProject.delete_by_slug(db, slug)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return result
