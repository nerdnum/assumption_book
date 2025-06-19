import xml.etree.ElementTree as ET
from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, String, or_, select
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, make_transient

from app.services.database import BaseEntity


class Document(BaseEntity):
    __tablename__ = "documents"
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    component_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("components.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=True)
    context: Mapped[str] = mapped_column(String(100), nullable=True)
    html_content: Mapped[str] = mapped_column(String, nullable=True)
    json_content: Mapped[JSON] = mapped_column(JSON, nullable=True)
    interface_id: Mapped[int] = mapped_column(Integer, nullable=True)
    origin: Mapped[JSON] = mapped_column(JSON, nullable=True)
    historic_id: Mapped[int] = mapped_column(Integer, nullable=True)

    @classmethod
    async def get_all(cls, db: AsyncSession) -> list["Document"]:
        documents = (await db.execute(select(cls))).scalars().all()
        return documents

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        project_id: int,
        component_id: int,
        title: str,
        sequence: int | None,
        context: str | None,
        html_content: str | None,
        json_content: dict | None,
        interface_id: int | None,
        user_id: int | None = None,
        origin: dict | None = None,
    ) -> "Document":
        document = cls(
            project_id=project_id,
            component_id=component_id,
            title=title,
            sequence=sequence,
            html_content=html_content,
            json_content=json_content,
            context=context,
            uuid=str(uuid4()),
            interface_id=interface_id,
            created_by=user_id,
            updated_by=user_id,
            origin=origin,
        )
        try:
            db.add(document)
            await db.commit()
            await db.refresh(document)
        except IntegrityError as error:
            await db.rollback()
            print("sql:create", error)
            raise ValueError("Document with this title already exists")
        return document

    @classmethod
    async def get_by_component_id(
        cls, db: AsyncSession, component_id: int
    ) -> list["Document"]:
        documents = (
            (
                await db.execute(
                    select(cls)
                    .where(cls.historic_id == None)
                    .filter(
                        or_(
                            cls.component_id == component_id,
                            cls.interface_id == component_id,
                        )
                    )
                    .order_by(Document.sequence)
                )
            )
            .scalars()
            .all()
        )
        return documents

    @classmethod
    async def get_by_document_id(
        cls,
        db: AsyncSession,
        document_id: int,
    ) -> "Document":
        try:
            document = await db.get(cls, document_id)
            if document is None:
                raise ValueError("Document not found")
        except ValueError as error:
            raise error
        return document

    @classmethod
    async def get_document_history_by_id(
        cls,
        db: AsyncSession,
        document_id: int,
    ) -> "Document":
        print("Looking for history of document with ID:", document_id)
        try:
            documents = (
                (
                    await db.execute(
                        select(cls)
                        .where(cls.historic_id == document_id)
                        .order_by(Document.updated_at.desc())
                    )
                )
                .scalars()
                .all()
            )
            if documents is None:
                raise ValueError("No history found")
            print("history length:", len(documents))
        except ValueError as error:
            raise error
        return documents

    @classmethod
    async def update_content_by_id(
        cls,
        db: AsyncSession,
        id: int,
        title: str | None,
        sequence: int | None,
        context: str | None,
        html_content: str | None,
        json_content: dict | None,
        interface_id: int | None,
        user_id: int | None = None,
    ) -> "Document":
        try:
            document = (
                (await db.execute(select(cls).filter(cls.id == id))).scalars().first()
            )

            if document is None:
                raise ValueError("Document not found")

            historic_document = cls(
                historic_id=document.id,
                project_id=document.project_id,
                component_id=document.component_id,
                title=document.title,
                sequence=document.sequence,
                context=document.context,
                html_content=document.html_content,
                json_content=document.json_content,
                interface_id=document.interface_id,
                origin=document.origin,
                created_by=document.created_by,
                updated_by=document.updated_by,
                uuid=str(uuid4()),
                created_at=document.created_at,
                updated_at=document.updated_at,
            )
            db.add(historic_document)  # Add the historic document to the session
            await db.commit()  # Commit the changes to the database
            # Clear the session to avoid stale data
            # document.id = None  # Reset the ID for a new instance
            # document.historic_id = id  # Set the historic ID to the old one
            # document.uuid = str(uuid4())  # Generate a new UUID
            # db.add(document)  # Add the new instance to the session
            # await db.commit()  # Commit the changes to the database
            if title is not None:
                document.title = title
            if sequence is not None:
                document.sequence = sequence
            if context is not None:
                document.context = context
            if html_content is not None:
                document.html_content = html_content
            if json_content is not None:
                document.json_content = json_content
            if interface_id is not None:
                document.interface_id = interface_id
            if user_id is not None:
                document.updated_by = user_id
            await db.commit()
            await db.refresh(document)
        except Exception as error:
            raise error
        return document

    @classmethod
    async def delete_by_id(cls, db: AsyncSession, document_id: int) -> None:
        # TODO: Add a check to see if the document is associated with a component
        try:
            document = await cls.get_by_document_id(db, document_id)
            if document is None:
                raise NoResultFound
            await db.delete(document)
            await db.commit()
        except NoResultFound:
            raise ValueError("Document not found")
        except Exception:
            raise
        return {"detail": "Document deleted"}

    @classmethod
    async def get_html_by_document_id(cls, db: AsyncSession, document_id: int) -> str:
        html = ""
        try:
            document = await db.get(cls, document_id)
            if document is None:
                raise ValueError("Document not found")
            html = f"<h2>{document.title}</h2>" + (document.html_content or "")
        except ValueError as error:
            raise error
        return html or ""
