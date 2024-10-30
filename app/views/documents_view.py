import os
import pprint
import uuid
from time import sleep
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
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
from app.sqlalchemy_models.components_sql import Component as SqlCompoment
from app.sqlalchemy_models.documents_sql import Document as SqlDocument
from app.sqlalchemy_models.projects_sql import Project as SqlProject

pp = pprint.PrettyPrinter(indent=4)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[Document], response_model_exclude_unset=True)
async def get_documents(
    project_id: int, component_id: int, db: AsyncSession = Depends(get_db)
):
    try:
        # check if project exists
        await SqlProject.get_by_id(db, project_id)
        # check if component exists
        await SqlCompoment.get_by_id(db, component_id)
        documents = await SqlDocument.get_by_ids(db, project_id, component_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    except ValueError as error:
        if str(error).find("not found"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    # sleep(3)
    return documents


@router.get(
    "/{document_id:int}", response_model=Document, response_model_exclude_unset=True
)
async def get_document_by_id(
    document_id: int, db: AsyncSession = Depends(get_db)
) -> Document:
    try:
        document = await SqlDocument.get_by_document_id(db, document_id)
    except ValueError as error:
        if str(error) == "Document not found":
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=400, detail=str(error))
    return document


# with ensure_request_validation_errors("body"):
#             await component.model_async_validate()
#         component = await SqlComponent.create(db, **component.model_dump())


@router.post(
    "", response_model=DocumentCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_document(
    document: DocumentCreate, db: AsyncSession = Depends(get_db)
) -> DocumentCreate:
    try:
        with ensure_request_validation_errors("body"):
            await document.model_async_validate()
        document = await SqlDocument.create(
            db, **document.model_dump(exclude_unset=True)
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return document


@router.put("/{document_id}", response_model=Document)
async def update_document(
    document_id: int, document: Document, db: AsyncSession = Depends(get_db)
):
    try:
        document = await SqlDocument.update_content_by_id(
            db, document_id, document.model_dump(exclude_unset=True)["content"]
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return document


@router.post("/upload_images")
async def create_upload_file(files: List[UploadFile]):
    filename_list = []
    for submitted_file in files:
        file_uuid = uuid.uuid4()
        name, ext = os.path.splitext(submitted_file.filename)
        new_file_name = f"{file_uuid}{ext}"
        cwd = os.getcwd()
        url_path = os.path.join("/", "static", "document_images", new_file_name)
        store_path = os.path.join(
            cwd, "app", "static", "document_images", new_file_name
        )
        with open(store_path, "wb") as local_file:
            result = local_file.write(await submitted_file.read())
            print(result)
        filename_list.append(url_path)

    return {"filenames": filename_list}


@router.delete("/{document_id}")
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await SqlDocument.delete_by_id(db, document_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return {"id": document_id, "status": "deleted"}
