import json
import os
from io import BytesIO

from lxml import etree
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_config
from app.html2docx.htmldocx import HtmlToDocx
from app.services.database import sessionmanager
from app.sqlalchemy_models.components_sql import Component as SqlComponent
from app.sqlalchemy_models.user_project_role_sql import Project as SqlProject


def processHtml(html):
    file_like_html = BytesIO(html.encode())
    tree = etree.parse(file_like_html, etree.HTMLParser())
    images = tree.xpath("//img")
    cwd = os.getcwd()
    if len(images) > 0:
        for image in images:
            src = image.attrib["src"]
            _, path = src.split("/static/document_images/")
            store_path = os.path.join(cwd, "app", "static", "document_images", path)
            image.attrib["src"] = store_path
    html_string = etree.tostring(tree).decode().replace("\n", "")
    return html_string


async def create_project_docx(spec):

    async with sessionmanager.session() as db:
        project = await SqlProject.get_project_by_id(db, spec.project_id)
        html = f'<p style="docx-style: Title"><strong>{project.title}</strong></p>'
        for component_spec in spec.components:
            component_html = await SqlComponent.get_html_by_id(db, component_spec.id)
            html += component_html

        final_html = processHtml(html)
        parser = HtmlToDocx()
        parser.table_style = "Grid Table 6 Colorful Accent 1"
        cwd = os.getcwd()
        template_path = os.path.join(cwd, "app", "static", "template.docx")
        docx = parser.parse_html_string(final_html, template=template_path)
        doc_name = f'project_{project.title.replace(" ", "_").lower()}'
        store_path = os.path.join(cwd, "app", "static", f"project_{doc_name}.docx")
        docx.save(store_path)
        store_path = os.path.join(cwd, "app", "static", f"project_{doc_name}.html")
        url_path = os.path.join("static", f"project_{doc_name}.docx")
        with open(store_path, "w") as file:
            file.write(final_html)

        return json.dumps(
            {"status": "success", "name": f"project_{doc_name}.docx", "url": url_path}
        )
