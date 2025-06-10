from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Union
from pydantic_async_validation.fastapi import ensure_request_validation_errors

from app.pydantic_models.risk_model import Risk, RiskCreate, RiskUpdate
from app.services.database import get_db
from app.sqlalchemy_models.risks_sql import Risk as SqlRisk
from app.sqlalchemy_models.user_project_role_sql import User as SqlUser
from app.views.auth_view import get_current_user_with_roles

from rich import print as pprint

router = APIRouter(prefix="/risks", tags=["risks"])


@router.get("", response_model=list[Risk])
async def get_risks(
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)],
    db: AsyncSession = Depends(get_db),
) -> list[Risk]:
    try:
        risks = await SqlRisk.get_all(db)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    return risks  # type: ignore


@router.post("", response_model=Risk | dict)
async def create_risks(
    risk_for_db: RiskCreate,
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)],
    db: AsyncSession = Depends(get_db),
) -> Risk | dict:
    try:
        risk_for_db.created_by = current_user.id
        with ensure_request_validation_errors("body"):
            await risk_for_db.model_async_validate()
        db_risk = await SqlRisk.create(db, **risk_for_db.model_dump())
    except (
        RequestValidationError
    ) as exp:  # This is required when running "ensure_request_validation_errors"
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=exp.errors(),
        )  # type: ignore
    except Exception as exp:
        raise HTTPException(status_code=400, detail=str(exp))
    return db_risk


@router.put("/{id}", response_model=Risk | dict)
async def update_risks(
    id: int,
    risk_for_db: RiskUpdate,
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)],
    db: AsyncSession = Depends(get_db),
) -> Risk | dict:
    try:
        risk_for_db.id = id
        risk_for_db.updated_by = current_user.id
        with ensure_request_validation_errors("body"):
            await risk_for_db.model_async_validate()
        db_risk = await SqlRisk.update(db, **risk_for_db.model_dump())
    except (
        RequestValidationError
    ) as exp:  # This is required when running "ensure_request_validation_errors"
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=exp.errors(),
        )  # type: ignore
    except Exception as exp:
        raise HTTPException(status_code=400, detail=str(exp))
    return db_risk
