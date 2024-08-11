from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database import get_db
from app.pydantic_models.element import Element, ElementCreate, ElementUpdate
from app.sqlalchemy_models.elements import Element as SqlElement


router = APIRouter(prefix="/elements", tags=["elements"])


@router.get("/", response_model=list[Element])
async def get_elements(db: AsyncSession = Depends(get_db)):
    elements = await SqlElement.get_all(db)
    return elements


@router.post("/", response_model=Element, status_code=status.HTTP_201_CREATED)
async def create_element(element: ElementCreate, db: AsyncSession = Depends(get_db)):
    try:
        element = await SqlElement.create(db, **element.model_dump())
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return element


@router.get("/{id}/", response_model=Element)
async def get_element(id: int, db: AsyncSession = Depends(get_db)):
    try:
        element = await SqlElement.get(db, id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return element


@router.put("/{id}/", response_model=Element)
async def update_element(id: int, element: ElementUpdate, db: AsyncSession = Depends(get_db)):
    try:
        element = await SqlElement.update(db, id, **element.model_dump())
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return element


@router.delete("/{id}/", response_model=None)
async def delete_element(id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await SqlElement.delete(db, id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail=str(error))
    return result
