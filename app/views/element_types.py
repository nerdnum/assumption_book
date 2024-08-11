from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database import get_db
from app.pydantic_models.element_type import ElementType, ElementTypeCreate, ElementTypeUpdate
from app.sqlalchemy_models.element_types import ElementType as SqlElementType


router = APIRouter(prefix="/element_types", tags=["element_types"])


@router.get("/", response_model=list[ElementType])
async def get_element_types(db: AsyncSession = Depends(get_db)):
    element_types = await SqlElementType.get_all(db)
    return element_types


@router.post("/", response_model=ElementType, status_code=status.HTTP_201_CREATED)
async def create_element_type(element_type: ElementTypeCreate, db: AsyncSession = Depends(get_db)):
    try:
        element_type = await SqlElementType.create(db, **element_type.model_dump())
    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return element_type


@router.get("/{id}/", response_model=ElementType)
async def get_element(id: int, db: AsyncSession = Depends(get_db)):
    try:
        element = await SqlElementType.get(db, id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return element


@router.put("/{id}/", response_model=ElementType)
async def update_element(id: int, element_type: ElementTypeUpdate, db: AsyncSession = Depends(get_db)):
    try:
        element_type = await SqlElementType.update(db, id, **element_type.model_dump())
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return element_type


@router.delete("/{id}/", response_model=None)
async def delete_element(id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await SqlElementType.delete(db, id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return result
