from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, String, func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.services.database import BaseEntity
from app.services.utils import translate_exception
from app.sqlalchemy_models.projects_sql import Project as SqlProject


class Component(AsyncAttrs, BaseEntity):
    __tablename__ = "components"
    # id, uuid, created_at, updated_at is in the BaseEntity
    parent_id = mapped_column(ForeignKey("components.id"))
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    uuid: Mapped[str] = mapped_column(String, nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    # is_template: Mapped[bool] = mapped_column(
    #     Boolean, nullable=False, default=False)
    descendants: Mapped[list["Component"]] = relationship("Component")

    # This check were moved to Pydantic Validations
    # __table_args__ = (
    #     UniqueConstraint("parent_id", "title"),
    #     CheckConstraint('length(title) > 5', name='title_length'), )

    @classmethod
    async def get_all(cls, db, project_id: int):
        return (
            (await db.execute(select(cls).where(cls.project_id == project_id)))
            .scalars()
            .all()
        )

    @classmethod
    async def get_root_components(cls, db, project_id: int):
        return (
            (
                await db.execute(
                    select(cls)
                    .where(cls.project_id == project_id)
                    .where(cls.parent_id == None)
                    .order_by(cls.sequence)
                )
            )
            .scalars()
            .all()
        )

    @classmethod
    async def create(
        cls,
        db,
        project_id: int,
        parent_id: int,
        title: str,
        level: int,
        sequence: int = None,
        description: str = None,
    ) -> "Component":

        project = await SqlProject.get_by_id(db, project_id)

        if sequence is None:
            max_sequence = (
                await db.execute(
                    select(func.max(cls.sequence))
                    .where(cls.project_id == project.id)
                    .where(cls.parent_id == parent_id)
                )
            ).scalar_one()
            if max_sequence is None:
                max_sequence = 0
        else:
            max_sequence = sequence

        component = cls(
            project_id=project_id,
            parent_id=parent_id,
            title=title,
            level=level,
            sequence=max_sequence + 1,
            description=description,
            uuid=str(uuid4()),
        )
        try:
            db.add(component)
            await db.commit()
            await db.refresh(component)
        except Exception as error:
            await db.rollback()
            exception = translate_exception(__name__, "create", error)
            raise exception
        return component

    @classmethod
    async def get_by_id(cls, db, component_id: int) -> "Component":
        # Component id is unique in the datatable so project_id is irrelevant
        try:
            component = await db.get(cls, component_id)

            if component is None:
                raise NoResultFound
        except NoResultFound:
            raise ValueError("component not found")
        except Exception as error:
            exception = translate_exception(__name__, "get", error)
            raise exception
        return component

    # 2024-06-30 although I am convinced that these worked before,
    # it does not anymore. It runs into a recursion error:
    # the first level of descendants are loaded, and can be accessed.
    # When you try to access a second level of descendants Python/SqlAlchemy
    # tries to load the descendants asynchronously, but out of context.
    # I solved the issue by create a dictionary and loading the descendants
    # into the dictionary recursively, then passing the dictionary to the
    # Pydantic model "ComponentWithDescendants".

    # @ classmethod
    # async def get_with_descendants_by_id(cls, db, component_id: int) -> "Component":
    #     try:
    #         component = (await db.execute(select(cls).where(cls.id == component_id)
    #                                       .options(selectinload(cls.descendants, recursion_depth=0))
    #                                       )).scalars().first()
    #         if component is None:
    #             raise NoResultFound
    #     except NoResultFound:
    #         raise ValueError("component not found")
    #     except Exception as error:
    #         exception = translate_exception(__name__, "get", error)
    #         raise exception
    #     return component

    # def __str__(self):
    #     return f"Component {self.id}: {self.title}"

    @classmethod
    async def update(
        cls,
        db,
        component_id: int,
        id: int,
        uuid: str,
        title: str = None,
        project_id: int = None,
        sequence: int = None,
        level: int = None,
        parent_id: int = None,
        description: str = None,
    ) -> "Component":
        component = await cls.get_by_id(db, component_id)

        if title is not None:
            component.title = title

        if project_id is not None:
            component.project_id = project_id

        if level is not None:
            component.level = level

        if parent_id is not None:
            component.parent_id = parent_id

        if description is not None:
            component.description = description

        if sequence is not None:
            component.sequence = sequence

        try:
            await db.commit()
            await db.refresh(component)
        except Exception as error:
            await db.rollback()
            exception = translate_exception(__name__, "update", error)
            raise exception
        return component

    @classmethod
    async def delete(cls, db, component_id: int) -> "Component":
        component = await cls.get_by_id(db, component_id)

        try:
            await db.delete(component)
            await db.commit()
        except Exception as error:
            await db.rollback()
            exception = translate_exception(__name__, "delete", error)
            raise exception
        return component

    @classmethod
    async def get_descendants(cls, db, component_id: int) -> list["Component"]:
        try:
            descendants = (
                (
                    await db.execute(
                        select(cls)
                        .where(cls.parent_id == component_id)
                        .order_by(cls.level, cls.sequence)
                    )
                )
                .scalars()
                .all()
            )
        except NoResultFound:
            raise ValueError("component not found")
        return descendants

    # @classmethod
    # async def get_hierarchy(cls, db, project_id: int, component_id: int = None, level: int = 0) -> any:
    #     # Ok as on 2024-06-25 11:53
    #     if component_id is not None:
    #         first_level = (await db.execute(select(cls)
    #                                         .where(cls.project_id == int(project_id))
    #                                         .where(cls.level == level)
    #                                         .order_by(cls.level, cls.sequence))).scalars().all()
    #     else:
    #         first_level = (await db.execute(select(cls)
    #                                         .where(cls.project_id == int(project_id))
    #                                         .where(cls.parent_id == component_id)
    #                                         .order_by(cls.level, cls.sequence))).scalars().all()

    #     for component in first_level:
    #         component.descendants = await cls.get_descendants(db, component.id)

    #     return first_level

    def __str__(self):
        return f"Component id={self.id}, title={self.title}, sequence={self.sequence}, project_id={self.project_id}"
