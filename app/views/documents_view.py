import os
import uuid
from time import sleep
from typing import List, Annotated
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic_async_validation.fastapi import ensure_request_validation_errors
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, label

from app.pydantic_models.document_model import (
    Document,
    DocumentCount,
    DocumentCreate,
    DocumentUpdate,
    DocumentWithUser,
)
from app.pydantic_models.user_model import User
from app.pydantic_models.component_model import ComponentCopyRecord

# App imports
from app.services.database import get_db
from app.sqlalchemy_models.components_sql import Component as SqlCompoment
from app.sqlalchemy_models.documents_sql import Document as SqlDocument
from app.sqlalchemy_models.user_project_role_sql import Project as SqlProject
from app.sqlalchemy_models.user_project_role_sql import User as SqlUser
from app.views.auth_view import get_current_user_with_roles
from app.services.database import sessionmanager
from app.services.utils import pretty_print

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/count", response_model=DocumentCount)
async def get_documents_count(
    project_id: int,
    component_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> DocumentCount:
    # TODO: add test of this endpoint
    try:
        # check if project exists
        await SqlProject.get_project_by_id(db, project_id)
        # check if component exists
        component = await SqlCompoment.get_by_id(db, component_id)
        if component.project_id != project_id:
            raise ValueError("Component not found")
        documents = await SqlDocument.get_by_component_id(db, component_id)
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
    return {
        "project_id": project_id,
        "component_id": component_id,
        "count": len(documents),
    }


@router.get(
    "", response_model=list[DocumentWithUser], response_model_exclude_unset=True
)
async def get_documents_by_component_id(
    component_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        # check if component exists
        await SqlCompoment.get_by_id(db, component_id)

        documents = (
            await db.execute(
                select(
                    SqlDocument.id,
                    SqlDocument.interface_id,
                    SqlDocument.uuid,
                    SqlDocument.project_id,
                    SqlDocument.component_id,
                    SqlDocument.title,
                    SqlDocument.sequence,
                    SqlDocument.context,
                    SqlDocument.html_content,
                    SqlDocument.json_content,
                    SqlDocument.id,
                    SqlDocument.uuid,
                    SqlDocument.updated_at,
                    SqlUser.id.label("updated_by_id"),
                    SqlUser.full_name.label("updated_by_full_name"),
                    SqlUser.email.label("updated_by_email"),
                )
                .join(SqlUser, SqlUser.id == SqlDocument.updated_by)
                .where(SqlDocument.component_id == component_id)
                .where(SqlDocument.historic_id == None)
                .order_by(SqlDocument.sequence)
            )
        ).all()
        # documents = await SqlDocument.get_by_component_id(db, component_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Component not found"
        )
    except ValueError as error:
        if str(error).find("not found"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    # sleep(3)
    return documents


@router.get("/{document_id:int}", response_model=DocumentWithUser)
async def get_document_by_id(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> Document:
    try:
        document = await SqlDocument.get_by_document_id(db, document_id)
        document_dict = document.__dict__

        document_dict["updated_by_id"] = current_user.id
        document_dict["updated_by_full_name"] = current_user.full_name
        document_dict["updated_by_email"] = current_user.email

    except ValueError as error:
        if str(error) == "Document not found":
            raise HTTPException(status_code=404, detail=str(error))

        raise HTTPException(status_code=400, detail=str(error))
    return document_dict


# with ensure_request_validation_errors("body"):
#             await component.model_async_validate()
#         component = await SqlComponent.create(db, **component.model_dump())


@router.post("", response_model=DocumentWithUser, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> DocumentCreate:
    try:
        with ensure_request_validation_errors("body"):
            await document.model_async_validate()
        document = await SqlDocument.create(
            db, **document.model_dump(), user_id=current_user.id
        )
        document_dict = document.__dict__

        document_dict["updated_by_id"] = current_user.id
        document_dict["updated_by_full_name"] = current_user.full_name
        document_dict["updated_by_email"] = current_user.email
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return document_dict


@router.put("/{document_id}", response_model=DocumentWithUser)
async def update_document(
    document_id: int,
    document: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    ## TODO: discrimate more between fields that are required for update
    ## all fields should be optional and can be updated
    ## test all fields of the document except document_id, project_id and component_id
    try:
        document_dict = document.model_dump()
        document = await SqlDocument.update_content_by_id(
            db,
            document_id,
            title=document_dict.get("title"),
            sequence=document_dict.get("sequence"),
            context=document_dict.get("context"),
            html_content=document_dict.get("html_content"),
            json_content=document_dict.get("json_content"),
            interface_id=document_dict.get("interface_id"),
            user_id=current_user.id,
        )
        document_dict = document.__dict__

        document_dict["updated_by_id"] = current_user.id
        document_dict["updated_by_full_name"] = current_user.full_name
        document_dict["updated_by_email"] = current_user.email
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return document_dict


@router.post("/upload_images")
async def create_upload_file(
    files: List[UploadFile],
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
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
        filename_list.append(url_path)

    return {"filenames": filename_list}


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
):
    try:
        await SqlDocument.delete_by_id(db, document_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return {"id": document_id, "status": "deleted"}


@router.get("/{document_id}/html")
async def get_document_html(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> str:
    try:
        document_html = await SqlDocument.get_html_by_document_id(db, document_id)
        # buf = html2docx(document_html, title="My Document")
        # cwd = os.getcwd()
        # store_path = os.path.join(cwd, "app", "static", f"document_{document_id}.docx")
        # with open(store_path, "wb") as fp:
        #     fp.write(buf.getvalue())
    except ValueError as error:
        if str(error) == "Document not found":
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=400, detail=str(error))
    return document_html


@router.get("/{document_id}/history", response_model=list[DocumentWithUser])
async def get_document_history(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> list[DocumentWithUser]:
    try:
        document_history = (
            await db.execute(
                select(
                    SqlDocument.id,
                    SqlDocument.interface_id,
                    SqlDocument.uuid,
                    SqlDocument.project_id,
                    SqlDocument.component_id,
                    SqlDocument.title,
                    SqlDocument.sequence,
                    SqlDocument.context,
                    SqlDocument.html_content,
                    SqlDocument.json_content,
                    SqlDocument.id,
                    SqlDocument.uuid,
                    SqlDocument.updated_at,
                    SqlUser.id.label("updated_by_id"),
                    SqlUser.full_name.label("updated_by_full_name"),
                    SqlUser.email.label("updated_by_email"),
                )
                .join(SqlUser, SqlUser.id == SqlDocument.updated_by)
                .where(SqlDocument.historic_id == document_id)
                .order_by(SqlDocument.updated_at.desc())
            )
        ).all()
    except ValueError as error:
        if str(error) == "No history found":
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=400, detail=str(error))
    return document_history


async def do_simple_copy(
    document: SqlDocument, project_id: int, component_id: int, user_id: int
):

    origin_dict = {
        "project_id": document.project_id,
        "component_id": document.component_id,
        "title": document.title,
        "sequence": document.sequence,
        "context": document.context,
        "interface_id": document.interface_id,
        "user_id": user_id,
    }

    new_document_dict = {
        "project_id": project_id,
        "component_id": component_id,
        "title": document.title,
        "sequence": document.sequence,
        "context": document.context,
        "html_content": document.html_content,
        "json_content": document.json_content,
        "interface_id": document.interface_id,
        "user_id": user_id,
        "origin": origin_dict,
    }
    async with sessionmanager.session() as db:
        new_document = await SqlDocument.create(db, **new_document_dict)
        return {
            "document_id": new_document.id,
            "component_id": component_id,
            "status": "copied",
        }


async def do_interface_copy(
    document: SqlDocument,
    project_id: int,
    component_id: int,
    copy_records: list[ComponentCopyRecord],
    user_id: int,
):

    interface_details = document.json_content.get("interfacedComponent", {})
    origin_dict = {
        "project_id": document.project_id,
        "component_id": document.component_id,
        "title": document.title,
        "sequence": document.sequence,
        "context": document.context,
        "interface_id": document.interface_id,
        "user_id": user_id,
        "interface_details": interface_details,
    }

    old_ids = {
        "componentOneId": interface_details.get("componentOneId"),
        "componentTwoId": interface_details.get("componentTwoId"),
    }
    new_ids = {
        "componentOneId": None,
        "componentTwoId": None,
    }
    new_interface_id = None

    copiesMade = 0
    copy_records_iter = iter(copy_records)
    while True:
        try:
            copy_record = next(copy_records_iter)
            if copy_record.from_id == document.interface_id:
                new_interface_id = copy_record.to_id
                copiesMade += 1
            if copy_record.from_id == old_ids["componentOneId"]:
                new_ids["componentOneId"] = copy_record.to_id
                copiesMade += 1
            if copy_record.from_id == old_ids["componentTwoId"]:
                new_ids["componentTwoId"] = copy_record.to_id
                copiesMade += 1
            if copiesMade == 3:
                break
        except StopIteration:
            break

    new_interface_details = interface_details.copy()
    new_interface_details["componentOneId"] = new_ids["componentOneId"]
    new_interface_details["componentTwoId"] = new_ids["componentTwoId"]
    if new_interface_details["componentOneId"] is None:
        new_interface_details["componentOneTitle"] = None
    if new_interface_details["componentTwoId"] is None:
        new_interface_details["componentTwoTitle"] = None
    new_json_content = document.json_content.copy()
    new_json_content["interfacedComponent"] = new_interface_details

    new_document_dict = {
        "project_id": project_id,
        "component_id": component_id,
        "title": document.title,
        "sequence": document.sequence,
        "context": document.context,
        "html_content": document.html_content,
        "json_content": new_json_content,
        "user_id": user_id,
        "interface_id": new_interface_id,
        "origin": origin_dict,
    }
    async with sessionmanager.session() as db:
        new_document = await SqlDocument.create(db, **new_document_dict)
        return {
            "document_id": new_document.id,
            "component_id": component_id,
            "status": "copied",
        }


@router.post("/copy", response_model=dict)
async def copy_documents(
    copy_records: list[ComponentCopyRecord],
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user_with_roles)] = None,
) -> None:
    """
    Copy documents from one component to another.
    """
    results = []
    for record in copy_records:
        pretty_print(record)
        if record.do_copy_documents:
            original_documents = await SqlDocument.get_by_component_id(
                db, record.from_id
            )
            if not original_documents:
                results.append(
                    {
                        "component_id": record.from_id,
                        "status": "no documents found",
                        "message": f"No documents found for component {record.from_id}",
                    }
                )
            for document in original_documents:
                if document.context == "interface":
                    result = await do_interface_copy(
                        document,
                        record.project_to_id,
                        record.to_id,
                        copy_records,
                        current_user.id,
                    )
                else:
                    result = await do_simple_copy(
                        document,
                        record.project_to_id,
                        record.to_id,
                        current_user.id,
                    )
                results.append(result)

    return {"status": "success", "results": results}
