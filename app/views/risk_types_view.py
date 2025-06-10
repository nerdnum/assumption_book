from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.pydantic_models.risk_type_model import RiskType, RiskTypeCreate, RiskTypeUpdate
from app.services.database import get_db
from app.sqlalchemy_models.risk_types_sql import RiskType as SqlRiskType
from app.sqlalchemy_models.user_project_role_sql import User as SqlUser
from app.views.auth_view import get_current_user_with_roles

router = APIRouter(prefix="/risk-types", tags=["risk-types"])


@router.get("", response_model=list[RiskType])
async def get_risk_types(
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)],
    db: AsyncSession = Depends(get_db),
) -> list[RiskType]:
    try:
        risk_types = await SqlRiskType.get_all(db)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    return risk_types


@router.post("", response_model=RiskType, status_code=status.HTTP_201_CREATED)
async def create_risk_type(
    risk_type_for_db: RiskTypeCreate,
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)],
    db: AsyncSession = Depends(get_db),
):
    try:
        risk_type_for_db.created_by = current_user.id
        db_risk_type = await SqlRiskType.create(db, **risk_type_for_db.model_dump())
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    return db_risk_type


@router.put("/{id}", response_model=RiskType)
async def update_risk_type(
    id: int,
    risk_type_for_db: RiskTypeUpdate,
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)],
    db: AsyncSession = Depends(get_db),
):
    try:
        risk_type_for_db.id = id
        risk_type_for_db.updated_by = current_user.id
        db_risk_type = await SqlRiskType.update(db, **risk_type_for_db.model_dump())
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    return db_risk_type


@router.delete("/{id}", response_model=dict)
async def delete_risk_type(
    id: int,
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)],
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await SqlRiskType.delete(db, id)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    return result
