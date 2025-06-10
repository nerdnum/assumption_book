from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.pydantic_models.risk_impact_model import (
    RiskImpact,
    RiskImpactCreate,
    RiskImpactUpdate,
)
from app.services.database import get_db
from app.sqlalchemy_models.user_project_role_sql import User as SqlUser
from app.sqlalchemy_models.risks_impacts_sql import RiskImpact as SqlRiskImpact
from app.views.auth_view import get_current_user_with_roles

router = APIRouter(prefix="/risk-impacts", tags=["risk-impacts"])


@router.get("", response_model=list[RiskImpact])
async def get_risk_impacts(
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)],
    db: AsyncSession = Depends(get_db),
) -> list[RiskImpact]:
    try:
        risk_impacts = await SqlRiskImpact.get_all(db)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    return risk_impacts


@router.get("categorized", response_model=list[RiskImpact])
async def get_risk_impacts(
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)],
    db: AsyncSession = Depends(get_db),
) -> list[RiskImpact]:
    try:
        risk_impacts = await SqlRiskImpact.get_all(db)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    return risk_impacts


@router.post("", response_model=RiskImpact, status_code=status.HTTP_201_CREATED)
async def create_risk_impact(
    risk_impact_for_db: RiskImpactCreate,
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)],
    db: AsyncSession = Depends(get_db),
):
    try:
        risk_impact_for_db.created_by = current_user.id
        db_risk_impact = await SqlRiskImpact.create(
            db, **risk_impact_for_db.model_dump()
        )
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    return db_risk_impact


@router.put("/{id}", response_model=RiskImpactUpdate)
async def update_risk_impact(
    id: int,
    risk_impact_for_db: RiskImpactUpdate,
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)],
    db: AsyncSession = Depends(get_db),
):
    try:
        risk_impact_for_db.id = id
        risk_impact_for_db.updated_by = current_user.id
        db_impact = await SqlRiskImpact.update(db, **risk_impact_for_db.model_dump())
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    return db_impact


@router.delete("/{id}", response_model=dict)
async def update_risk_impact(
    id: int,
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)],
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        result = await SqlRiskImpact.delete(db, id)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    return result
