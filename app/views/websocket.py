import json
from typing import Annotated

from fastapi import APIRouter, WebSocket, Depends
from starlette.websockets import WebSocketDisconnect

from app.pydantic_models.project_model import DocSpec
from app.sqlalchemy_models.user_project_role_sql import User as SqlUser
from app.views.auth_view import get_current_user_with_roles
from app.services.create_docx import create_project_docx, create_project_xlsx

router = APIRouter(prefix="/ws", tags=["websocket"])

valid_types = ["create_document"]


async def process_data(websocket, message):
    try:
        json_message = json.loads(message)
        message_type = json_message.get("type")
        document_type = json_message.get("documentType")
        if message_type is None:
            await websocket.send_text(str({"error": "No message type provided"}))
            return
        if message_type not in valid_types:
            await websocket.send_text(str({"error": "Unknown message type"}))
            return
        if message_type == "create_document":

            doc_spec = DocSpec.model_validate_json(message)
            document_meta = None
            if document_type == "docx":
                document_meta = await create_project_docx(doc_spec)
            elif document_type == "xlsx":
                document_meta = await create_project_xlsx(doc_spec)
            await websocket.send_text(str(document_meta))
            return
    except json.JSONDecodeError as error:
        await websocket.send_text(str({"error": error}))
        return


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
):

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "close":
                await websocket.close(1000, "Server closed socket")
                break
            await process_data(websocket, data)

    except WebSocketDisconnect:
        pass
