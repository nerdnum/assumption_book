import pprint

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic_async_validation.fastapi import ensure_request_validation_errors
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.pydantic_models.document_model import (
    Document,
    DocumentCreate,
    DocumentCreateResponse,
)

# App imports
from app.services.database import get_db
from app.sqlalchemy_models.document_sql import Document as SqlDocument
from app.sqlalchemy_models.projects_sql import Project as SqlProject

pp = pprint.PrettyPrinter(indent=4)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[Document])
async def get_documents(
    project_id: int, component_id: int, db: AsyncSession = Depends(get_db)
):
    try:
        # check if project exists
        await SqlProject.get_by_id(db, project_id)
        documents = await SqlDocument.get_by_ids(db, project_id, component_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return documents


# with ensure_request_validation_errors("body"):
#             await component.model_async_validate()
#         component = await SqlComponent.create(db, **component.model_dump())


@router.post("", response_model=DocumentCreateResponse)
async def create_document(
    document: DocumentCreate, db: AsyncSession = Depends(get_db)
) -> DocumentCreate:
    try:
        document = await SqlDocument.create(db, **document.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return document
