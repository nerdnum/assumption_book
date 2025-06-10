from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.pydantic_models.risk_probability_model import (
    RiskProbability,
    RiskProbabilityCreate,
    RiskProbabilityUpdate,
)
from app.services.database import get_db
from app.sqlalchemy_models.user_project_role_sql import User as SqlUser
from app.sqlalchemy_models.risk_probabilities_sql import (
    RiskProbability as SqlRiskProbability,
)
from app.views.auth_view import get_current_user_with_roles

router = APIRouter(prefix="/risk-probabilities", tags=["risk-probabilities"])


@router.get("", response_model=list[RiskProbability])
async def get_probabilities(
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)],
    db: AsyncSession = Depends(get_db),
) -> list[RiskProbability]:
    try:
        probabilities = await SqlRiskProbability.get_all(db)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    return probabilities  # type: ignore


@router.post("", response_model=RiskProbability, status_code=status.HTTP_201_CREATED)
async def create_risk_probability(
    probability_for_db: RiskProbabilityCreate,
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)],
    db: AsyncSession = Depends(get_db),
):
    try:
        probability_for_db.created_by = current_user.id
        db_probability = await SqlRiskProbability.create(
            db, **probability_for_db.model_dump()
        )
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    return db_probability


@router.put(
    "/{id}", response_model=RiskProbability, status_code=status.HTTP_201_CREATED
)
async def update_risk_probability(
    id: int,
    probability_for_db: RiskProbabilityUpdate,
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)],
    db: AsyncSession = Depends(get_db),
):
    try:
        probability_for_db.id = id
        probability_for_db.updated_by = current_user.id
        db_probability = await SqlRiskProbability.update(
            db, **probability_for_db.model_dump()
        )
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    return db_probability


@router.delete("/{id}")
async def delete_risk_probability(
    id: int,
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)],
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await SqlRiskProbability.delete(db, id)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    return result
