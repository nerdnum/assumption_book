import os
import pprint
from typing import AnyStr

from fastapi import APIRouter

# from html2docx import html2docx

# from app.pydantic_models.document_model import DocHtml

pp = pprint.PrettyPrinter(indent=4)

router = APIRouter(prefix="/doc_export", tags=["doc_export"])


@router.post("/export")
async def export_doc(document: str) -> AnyStr:
    # buf = html2docx(doc_html.html, "test.docx")
    # print(os.getcwd())
    # print(document.html)
    # with open("test.html", "w") as f:
    #     f.write(document.html)
    return "all ok"
