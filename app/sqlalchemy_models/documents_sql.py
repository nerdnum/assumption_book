from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, String, select
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

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
    content: Mapped[JSON] = mapped_column(JSON, nullable=True)

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
        content: dict | None,
    ) -> "Document":
        document = cls(
            project_id=project_id,
            component_id=component_id,
            title=title,
            sequence=sequence,
            content=content,
            context=context,
            uuid=str(uuid4()),
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
    async def get_by_ids(
        cls, db: AsyncSession, project_id: int, component_id: int
    ) -> list["Document"]:
        document = (
            (
                await db.execute(
                    select(cls).filter(
                        cls.project_id == project_id, cls.component_id == component_id
                    )
                )
            )
            .scalars()
            .all()
        )
        return document

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
    async def update_content_by_id(
        cls,
        db: AsyncSession,
        id: int,
        content: dict | None,
    ) -> "Document":
        try:
            document = (
                (await db.execute(select(cls).filter(cls.id == id))).scalars().first()
            )
            document.content = content
            await db.commit()
            await db.refresh(document)
        except Exception as error:
            raise error
        return document

    @classmethod
    async def delete_by_id(cls, db: AsyncSession, document_id: int) -> None:
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
