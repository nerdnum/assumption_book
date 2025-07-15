# Standard libary imports
from typing import List, Optional, Sequence
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    select,
)
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

# App imports
from app.services.database import BaseEntity


class ProjectRole(BaseEntity):
    __tablename__ = "project_roles"
    __table_args__ = (UniqueConstraint("project_id", "role_id"),)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id"), nullable=False
    )

    def __repr__(self):
        return f"<ProjectRole id:{self.id}, project_id:{self.project_id}, role_id:{self.role_id}>"


class UserProject(BaseEntity):
    "Projects that a user can access."

    __tablename__ = "user_projects"
    __table_args__ = (UniqueConstraint("user_id", "project_id"),)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )

    # user: Mapped["User"] = relationship(back_populates="projects", lazy="selectin")
    # projects: Mapped["Project"] = relationship(back_populates="users", lazy="selectin")
    def __repr__(self):
        return f"<UserProject id:{self.id} user_id:{self.user_id}, project_id:{self.project_id}>"


class UserProjectRole(BaseEntity):
    "Kinds of user roles that can be associated with a project."

    __tablename__ = "user_project_roles"
    __table_args__ = (UniqueConstraint("user_id", "project_role_id"),)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    project_role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("project_roles.id"), nullable=False
    )

    def __repr__(self):
        return f"<UserProjectRole id:{self.id}, user_id:{self.user_id}, project_role_id:{self.project_role_id}>"

    # @classmethod
    # async def create(
    #     cls, db: AsyncSession, user_id: int, user_id_for_role: int, project_role_id: int
    # ) -> "UserProjectRole":
    #     try:
    #         user_project_role = cls(
    #             user_id=user_id_for_role,
    #             project_role_id=project_role_id,
    #             uuid=str(uuid4()),
    #             created_by=user_id,
    #             updated_by=user_id,
    #         )
    #         db.add(user_project_role)
    #         await db.commit()
    #         await db.refresh(user_project_role)
    #     except IntegrityError as error:
    #         print("yes, here")
    #         await db.rollback()
    #         if (
    #             'duplicate key value violates unique constraint "user_project_roles_user_id_project_role_id_key"'
    #             in str(error)
    #         ):
    #             raise ValueError("User -> Project -> Role association already exists")
    #         raise error
    #     return user_project_role

    # @classmethod
    # async def get_user_roles_for_a_specific_project(
    #     cls, db: AsyncSession, project_id: int, user_id: int
    # ) -> Sequence["UserProjectRole"]:
    #     try:
    #         user_project_roles = (
    #             await db.execute(
    #                 select(
    #                     cls.id.label("user_project_role_id"),
    #                     cls.user_id,
    #                     ProjectRole.id.label("project_role_id"),
    #                     ProjectRole.project_id,
    #                 )
    #                 .join(ProjectRole, cls.project_role_id == ProjectRole.id)
    #                 .where(cls.user_id == user_id, ProjectRole.project_id == project_id)
    #             )
    #         ).all()
    #     except Exception as error:
    #         raise error
    #     return user_project_roles

    # @classmethod
    # async def delete(cls, db, user_id, project_role_id):
    #     try:
    #         user_project_role = (
    #             await db.execute(
    #                 select(cls)
    #                 .where(cls.user_id == user_id)
    #                 .where(cls.project_role_id == project_role_id)
    #             )
    #         ).scalar_one_or_none()
    #         if user_project_role is None:
    #             raise ValueError("User project role does not exist.")
    #         await db.delete(user_project_role)
    #         await db.commit()
    #         return {"detail": "success"}
    #     except ValueError:
    #         await db.rollback()
    #         raise
    #     except Exception:
    #         raise


class UserSystemRole(BaseEntity):
    """
    Project roles assigned to a user."""

    __tablename__ = "user_system_roles"
    __table_args__ = (UniqueConstraint("user_id", "system_role_id"),)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    system_role_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("roles.id"),
        nullable=True,
    )

    def __repr__(self):
        return f"<SystemRole id:{self.id}, user_id:{self.user_id}, system_role_id:{self.system_role_id}>"

    # @classmethod
    # async def get_project_role_by_id(
    #     cls, db: AsyncSession, project_role_id: int
    # ) -> "ProjectRole":
    #     try:
    #         project_role = await ProjectRole.get(db, project_role_id)
    #         if project_role is None:
    #             raise NoResultFound("Project role not found")
    #         return project_role.scalar_one()
    #     except NoResultFound:
    #         return None

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        user_id: int,
        user_id_for_role: int,
        system_role_id: int,
    ) -> "UserSystemRole":
        try:
            user = await User.get(db, user_id_for_role)
            if not user:
                raise ValueError("User not found")

            system_role = await Role.get(db, system_role_id)
            if not system_role:
                raise ValueError("System role not found")

            user_system_role = cls(
                user_id=user_id_for_role,
                system_role_id=system_role_id,
                uuid=str(uuid4()),
                created_by=user_id,
                updated_by=user_id,
            )
            db.add(user_system_role)
            await db.commit()
            await db.refresh(user_system_role)
            return user_system_role

        except IntegrityError as error:
            await db.rollback()
            raise ValueError("User -> System -> Role association already exists")
        except Exception:
            raise

    # @classmethod
    # async def delete(
    #     cls,
    #     db: AsyncSession,
    #     user_id: int,
    #     system_role_id: int,
    #     current_user_id: int,
    # ) -> "UserSystemRole":
    #     try:
    #         user_project_role = (
    #             (
    #                 await db.execute(
    #                     select(cls).where(
    #                         cls.user_id == user_id,
    #                         cls.project_role_id == system_role_id,
    #                     )
    #                 )
    #             )
    #             .scalars()
    #             .first()
    #         )
    #         if not user_project_role:
    #             raise ValueError("User project role not found")

    #         await db.delete(user_project_role)
    #         await db.commit()
    #     except Exception:
    #         await db.rollback()
    #         raise
    #     return user_project_role

    # @classmethod
    # async def get_user_roles_accross_all_projects(
    #     cls, db: AsyncSession, user_id: int
    # ) -> Sequence["UserSystemRole"]:
    #     try:
    #         user = await User.get(db, user_id)
    #         if not user:
    #             raise ValueError("User not found")

    #         user_roles = (
    #             (await db.execute(select(cls).where(cls.user_id == user_id)))
    #             .scalars()
    #             .all()
    #         )
    #     except Exception as error:
    #         raise error
    #     return user_roles

    # @classmethod
    # async def get_user_roles_for_a_specific_project(
    #     cls, db: AsyncSession, project_id: int, user_id: int
    # ) -> Sequence["UserSystemRole"]:
    #     try:

    #         project = await Project.get_project_by_id(db, project_id)
    #         if not project:
    #             raise ValueError("Project not found")

    #         user_roles = (
    #             await db.execute(
    #                 select(
    #                     cls.id,
    #                     cls.user_id,
    #                     cls.project_role_id,
    #                     cls.system_role_id,
    #                     UserProjectRole.project_id,
    #                 )
    #                 .join(UserProjectRole, cls.project_role_id == UserProjectRole.id)
    #                 .where(cls.user_id == user_id)
    #                 .where(UserProjectRole.project_id == project_id)
    #             )
    #         ).all()
    #     except Exception as error:
    #         raise error
    #     return user_roles


###--------------------- User ---------------------###


class User(BaseEntity):
    """User model represents a user in the system.
    It includes fields for username, full name, preferred name, email, password, and various flags for user status.
    It also has relationships to projects through UserProject and roles through UserRole.
    """

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    preferred_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[Optional[str]] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)
    is_first_login: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    updated_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    projects: Mapped[List["Project"]] = relationship(
        secondary=UserProject.__table__,
        lazy="selectin",
        back_populates="users",
        primaryjoin="UserProject.user_id == User.id",
        secondaryjoin="UserProject.project_id == Project.id",
        join_depth=2,
    )
    system_roles: Mapped[List["Role"]] = relationship(
        secondary=UserSystemRole.__table__,
        lazy="selectin",
        back_populates="system_users",
        primaryjoin="UserSystemRole.user_id == User.id",
        secondaryjoin="and_(UserSystemRole.system_role_id == Role.id)",
        join_depth=2,
    )
    project_roles: Mapped[List["Role"]] = relationship(
        secondary=UserProjectRole.__table__,
        lazy="selectin",
        primaryjoin="UserProjectRole.user_id == User.id",
        secondaryjoin="and_(UserProjectRole.project_role_id == Role.id)",
        back_populates="project_users",
    )

    def __repr__(self):
        return f"<User {self.id}: username={self.username}, email={self.email}>"

    @classmethod
    async def get(cls, db: AsyncSession, id: int) -> "User":
        try:
            # This line returns the user with their associated projects.
            # It is now necessary to fill in their project roles to make
            # the record useful and complete for the frontend.
            user = await db.get(cls, id, options=[selectinload(cls.projects)])
            if not user:
                raise ValueError("User not found")
        except Exception:
            raise
        return user

    @classmethod
    async def get_all(cls, db: AsyncSession) -> Sequence["User"]:
        """Get all users from the database."""
        users = (await db.execute(select(cls))).scalars().all()
        return users

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        user_id: int,
        full_name: str,
        preferred_name: str | None,
        email: str,
        is_active: bool = True,
        is_superuser: bool = False,
        is_first_login: bool = True,
        username: str | None = None,
    ) -> "User":
        user = cls(
            full_name=full_name,
            username=username,
            preferred_name=preferred_name,
            email=email,
            is_active=is_active,
            is_superuser=is_superuser,
            is_first_login=is_first_login,
            uuid=str(uuid4()),
            created_by=user_id,
            updated_by=user_id,
        )

        try:
            db.add(user)
            await db.commit()
            await db.refresh(user)
        except IntegrityError:
            await db.rollback()
            raise ValueError("User with that email already exists")
        except Exception:
            await db.rollback()
            raise
        return user

    # This method does not make sense here, it should be under projects
    # @classmethod
    # async def get_user_roles_for_all_projects(cls, db: AsyncSession, id: int) -> "User":
    #     try:
    #         user = await db.get(cls, id)
    #         if not user:
    #             raise ValueError("User not found")

    #         user_project_roles = await UserProjectRole.get_user_roles(db, id)
    #         role_definitions = []
    #         for role in user_project_roles:
    #             role_definitions.append((role.user_id, role.role_id, role.project_id))

    #         if user.projects:
    #             for project in user.projects:
    #                 possible_roles = project.roles
    #                 project.roles = []
    #                 for role in possible_roles:
    #                     role_definition = (id, role.id, project.id)
    #                     if role_definition in role_definitions:
    #                         project.roles.append(role)

    #     except Exception as error:
    #         raise error

    #     return user

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        user_id: int,
        id: int,
        full_name: str | None,
        username: str | None,
        preferred_name: str | None,
        email: str | None,
        is_active: bool | None,
        is_superuser: bool | None,
        system_roles: List["Role"] | None = None,
    ) -> "User":
        try:
            user = await cls.get(db, id)
            if full_name:
                user.full_name = full_name
            if username:
                user.username = username
            if preferred_name:
                user.preferred_name = preferred_name
            if email:
                user.email = email
            if is_active is not None:
                user.is_active = is_active
            if is_superuser is not None:
                user.is_superuser = is_superuser
            user.updated_by = user_id
            try:
                await db.commit()
                await db.refresh(user)
            except IntegrityError:
                await db.rollback()
                raise ValueError("User with that email already exists")
            if system_roles is not None:
                # Clear existing system roles
                requested_role_ids = {role.id for role in system_roles}
                roles_to_remove = []

                user_system_roles = (
                    (
                        await db.execute(
                            select(UserSystemRole).where(
                                UserSystemRole.user_id == user.id
                            )
                        )
                    )
                    .scalars()
                    .all()
                )

                for user_role in user_system_roles:
                    if user_role.system_role_id not in requested_role_ids:
                        roles_to_remove.append(user_role)
                    else:
                        requested_role_ids.remove(user_role.system_role_id)

                for role in roles_to_remove:
                    await db.delete(role)
                    await db.commit()

                # Add new system roles
                for role_id in requested_role_ids:
                    user_system_role = UserSystemRole(
                        user_id=id,
                        system_role_id=role_id,
                        uuid=str(uuid4()),
                        created_by=user_id,
                        updated_by=user_id,
                    )
                    db.add(user_system_role)
                await db.commit()
                await db.refresh(user)
        except NoResultFound:
            raise ValueError("User not found")
        except Exception:
            await db.rollback()
            raise
        return user

    @classmethod
    async def set_password(
        cls, db: AsyncSession, user_id: int, id: int, hashed_password: str | None
    ) -> "User":
        try:
            user = await cls.get(db, id)
            if hashed_password:
                user.password = hashed_password
                user.updated_by = user_id
                await db.commit()
                await db.refresh(user)
        except Exception:
            await db.rollback()
            raise
        return user

    @classmethod
    async def delete(cls, db: AsyncSession, id: int) -> None:
        try:
            user = await cls.get(db, id)
            if user is None:
                raise NoResultFound
            await db.delete(user)
            await db.commit()
        except NoResultFound:
            raise ValueError("User not found")
        return {"detail": "User deleted"}

    @classmethod
    async def get_user_by_uuid(cls, db: AsyncSession, uuid: uuid4) -> "User":
        try:
            user = (
                (await db.execute(select(cls).where(cls.uuid == uuid)))
                .scalars()
                .first()
            )
            if not user:
                raise NoResultFound
        except NoResultFound:
            raise ValueError("User not found")
        return user

    @classmethod
    async def get_user_by_username(cls, db: AsyncSession, username: str) -> "User":
        try:
            user = (
                (await db.execute(select(cls).where(cls.username == username)))
                .scalars()
                .first()
            )
            if not user:
                raise NoResultFound
        except NoResultFound:
            raise ValueError("User not found")
        return user

    @classmethod
    async def get_user_by_email(cls, db: AsyncSession, email: str) -> "User":
        try:
            user = (
                (await db.execute(select(cls).where(cls.email == email)))
                .scalars()
                .first()
            )
            if not user:
                raise NoResultFound
        except NoResultFound:
            raise ValueError("User not found")
        return user

    @classmethod
    async def activate(cls, db: AsyncSession, user_id: int, id: int) -> "User":
        try:
            user = await cls.get(db, id)
            user.is_active = True
            user.updated_by = user_id
            await db.commit()
            await db.refresh(user)
        except Exception:
            await db.rollback()
            raise
        return user

    @classmethod
    async def deactivate(cls, db: AsyncSession, user_id: int, id: int) -> "User":
        try:
            user = await cls.get(db, id)
            user.is_active = False
            user.updated_by = user_id
            await db.commit()
            await db.refresh(user)
        except Exception:
            await db.rollback()
            raise
        return user


###--------------------- Project ---------------------###


class Project(BaseEntity):
    __tablename__ = "projects"
    title: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    project_manager: Mapped[str] = mapped_column(String(100), nullable=True)
    logo_url: Mapped[str] = mapped_column(String(255), nullable=True)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    users: Mapped[List[User]] = relationship(
        secondary=UserProject.__table__,
        lazy="selectin",
        back_populates="projects",
    )
    # I've selected to report user with their projects and the roles the have in those projects.
    # This relationship however provides ALL the roles that is assciated with a project,
    # but a user cannot have all those roles in a project, so this relationship has to
    # be filtered when the user is fetched.
    project_roles: Mapped[List["Role"]] = relationship(
        secondary=ProjectRole.__table__,
        lazy="selectin",
        back_populates="projects",
        primaryjoin="ProjectRole.project_id == Project.id",
        secondaryjoin="and_(ProjectRole.role_id == Role.id)",
    )

    def __repr__(self):
        return f"<Project {self.id}: title={self.title}>"

    @classmethod
    async def get_all(cls, db: AsyncSession) -> Sequence["Project"]:
        projects = (await db.execute(select(cls).order_by(cls.title))).scalars().all()
        return projects

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        user_id: int,
        title: str,
        description: str | None = None,
        project_manager: str | None = None,
        logo_url: str | None = None,
        image_url: str | None = None,
    ) -> "Project":

        project = cls(
            title=title,
            description=description,
            project_manager=project_manager,
            logo_url=logo_url,
            image_url=image_url,
            uuid=str(uuid4()),
            created_by=user_id,
            updated_by=user_id,
        )

        try:
            db.add(project)
            await db.commit()
            await db.refresh(project)

            possible_project_roles = (
                (await db.execute(select(Role).where(Role.is_system_role == False)))
                .scalars()
                .all()
            )
            for role in possible_project_roles:
                project_role = ProjectRole(
                    project_id=project.id,
                    role_id=role.id,
                    uuid=str(uuid4()),
                    created_by=user_id,
                    updated_by=user_id,
                )
                db.add(project_role)
            await db.commit()

            await db.refresh(project)

            new_project_roles_ids = (
                (
                    await db.execute(
                        select(ProjectRole.id).where(
                            ProjectRole.project_id == project.id
                        )
                    )
                )
                .scalars()
                .all()
            )

            for new_project_role_id in new_project_roles_ids:
                user_project_role = UserProjectRole(
                    user_id=user_id,
                    project_role_id=new_project_role_id,
                    uuid=str(uuid4()),
                    created_by=user_id,
                    updated_by=user_id,
                )
                db.add(user_project_role)
            await db.commit()

        except IntegrityError as error:
            await db.rollback()
            if (
                'duplicate key value violates unique constraint "projects_title_key"'
                in str(error)
            ):
                # This is a specific error for duplicate project titles
                raise ValueError(
                    "A project with this title already exists. You may not have access."
                )
            raise error
        return project

    @classmethod
    async def get_project_by_id(cls, db: AsyncSession, id: int) -> "Project":
        try:
            project = await db.get(cls, id)
            if project is None:
                raise ValueError("Project not found")
        except Exception as error:
            raise error

        return project

    @classmethod
    async def update_project(
        cls,
        db: AsyncSession,
        user_id: int,
        id: int,
        title: str | None,
        description: str | None,
        project_manager: str | None,
        logo_url: str | None,
        image_url: str | None,
    ) -> "Project":
        try:
            project = await db.get(cls, id)
            if title is not None:
                project.title = title
            if description is not None:
                project.description = description
            if project_manager is not None:
                project.project_manager = project_manager
            if logo_url is not None:
                project.logo_url = logo_url
            if image_url is not None:
                project.image_url = image_url
            project.updated_by = user_id
            try:
                await db.commit()
                await db.refresh(project)
            except IntegrityError:
                await db.rollback()
                raise ValueError("Project with this title already exists")

            possible_roles_ids = (
                (
                    (
                        await db.execute(
                            select(Role.id).where(Role.is_system_role == False)
                        )
                    )
                )
                .scalars()
                .all()
            )
            project_role_ids = (
                (
                    await db.execute(
                        select(ProjectRole.role_id).where(ProjectRole.project_id == id)
                    )
                )
                .scalars()
                .all()
            )
            roles_to_add = [
                role_id
                for role_id in possible_roles_ids
                if role_id not in project_role_ids
            ]
            for role_id in roles_to_add:
                project_role = ProjectRole(
                    project_id=id,
                    role_id=role_id,
                    uuid=str(uuid4()),
                    created_by=user_id,
                    updated_by=user_id,
                )
                db.add(project_role)
            await db.commit()
            await db.refresh(project)
        except (
            IntegrityError
        ) as error:  # Catching IntegrityError for duplicate project titles
            await db.rollback()
            if (
                'duplicate key value violates unique constraint "projects_title_key"'
                in str(error)
            ):
                raise ValueError(
                    "A project with this title already exists. You may not have access."
                )
            raise error
        except NoResultFound:
            raise ValueError("Project not found")
        return project

    @classmethod
    async def update_by_id(
        cls,
        db: AsyncSession,
        user_id: int,
        id: int,
        title: str | None,
        description: str | None,
        project_manager: str | None,
        logo_url: str | None,
        image_url: str | None,
    ) -> "Project":
        return await cls.update_project(
            db, user_id, id, title, description, project_manager, logo_url, image_url
        )

    @classmethod
    async def delete_by_id(cls, db: AsyncSession, id: int) -> "Project":
        try:
            project = await db.get(cls, id)
            if project is None:
                raise NoResultFound
            await db.delete(project)
            await db.commit()
        except NoResultFound:
            raise ValueError("Project not found")
        return project

    @classmethod
    async def add_project_role(
        cls, db: AsyncSession, user_id: int, project_id: int, project_role_id: int
    ) -> "Project":
        duplicate_error_check = None
        try:
            project = await cls.get_project_by_id(db, project_id)
            if project is None:
                raise ValueError("Project not found")
            role = await Role.get(db, project_role_id)
            if role is None:
                raise ValueError("Role not found")
            if role.is_system_role:
                raise ValueError(
                    "This role is a system role and cannot be added to a project"
                )
            project_role = ProjectRole(
                project_id=project_id,
                role_id=project_role_id,
                uuid=str(uuid4()),
                created_by=user_id,
                updated_by=user_id,
            )
            duplicate_error_check = f"DETAIL:  Key (project_id, project_role_id)=({project.id}, {project_role_id}) already exists"
            db.add(project_role)
            await db.commit()
            await db.refresh(project)
        except ValueError as error:
            await db.rollback()
            raise error
        except Exception as error:
            if (
                duplicate_error_check
                and duplicate_error_check in str(error)
                or 'duplicate key value violates unique constraint "project_roles_project_id_role_id_key"'
                in str(error)
            ):
                await db.rollback()
                raise ValueError("This role is already associated with this project")
            raise error
        return project

    # @classmethod
    # async def get_all_projects_with_all_its_associcated_roles(
    #     cls, db: AsyncSession, project_id: int, role_id: int, user_id: int
    # ) -> "Project":
    #     pass

    # @classmethod
    # async def get_a_projects_with_its_associcated_roles(
    #     cls, db: AsyncSession, project_id: int, role_id: int, user_id: int
    # ) -> "Project":
    #     pass


###--------------------- Role ---------------------###


class Role(BaseEntity):
    __tablename__ = "roles"
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=False)
    system_users: Mapped[List["User"]] = relationship(
        secondary=UserSystemRole.__table__,
        back_populates="system_roles",
        lazy="selectin",
        primaryjoin="UserSystemRole.system_role_id == Role.id",
        secondaryjoin="UserSystemRole.user_id == User.id",
        join_depth=1,
    )
    project_users: Mapped[List["User"]] = relationship(
        secondary=UserProjectRole.__table__,
        back_populates="project_roles",
        lazy="selectin",
        primaryjoin="UserProjectRole.project_role_id == Role.id",
        secondaryjoin="and_(UserProjectRole.user_id == User.id)",
        join_depth=1,
    )
    projects: Mapped[List["Project"]] = relationship(
        secondary=ProjectRole.__table__,
        back_populates="project_roles",
        lazy="selectin",
        primaryjoin="ProjectRole.role_id == Role.id",
        secondaryjoin="ProjectRole.project_id == Project.id",
    )

    def __repr__(self):
        return f"<Role {self.id}: title={self.name}>"

    @classmethod
    async def get_all(cls, db: AsyncSession) -> Sequence["Role"]:
        roles = (await db.execute(select(cls))).scalars().all()
        return roles

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        user_id: int,
        name: str,
        description: str | None = None,
        is_active: bool = True,
        is_system_role: bool = False,
    ) -> "Role":
        role = cls(
            name=name,
            description=description,
            is_active=is_active,
            is_system_role=is_system_role,
            uuid=str(uuid4()),
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(role)
        try:
            await db.commit()
            await db.refresh(role)
        except IntegrityError:
            await db.rollback()
            raise ValueError("Role with that name already exists")
        return role

    @classmethod
    async def get(cls, db: AsyncSession, id: int) -> "Role":
        try:
            role = await db.get(cls, id)
            if not role:
                raise NoResultFound
        except NoResultFound:
            raise ValueError("Role not found")
        return role

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        user_id: int,
        id: int,
        name: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
        is_system_role: bool | None = None,
    ) -> "Role":
        try:
            role = await cls.get(db, id)
            if name is not None:
                role.name = name
            if description is not None:
                role.description = description
            if is_active is not None:
                role.is_active = is_active
            if is_system_role is not None:
                role.is_system_role = is_system_role
            role.updated_by = user_id
            try:
                await db.commit()
                await db.refresh(role)
            except IntegrityError:
                await db.rollback()
                raise ValueError("Role with that name already exists")
        except Exception:
            await db.rollback()
            raise
        return role

    @classmethod
    async def delete(cls, db: AsyncSession, id: int) -> None:
        try:
            role = await cls.get(db, id)
            await db.delete(role)
            await db.commit()
        except NoResultFound:
            raise ValueError("Role not found")
        return {"detail": "Role deleted"}

    @classmethod
    async def get_role_by_uuid(cls, db: AsyncSession, uuid: str) -> "Role":
        try:
            roles = (
                (await db.execute(select(cls).where(cls.uuid == uuid))).scalars().all()
            )
            if len(roles) == 0:
                raise NoResultFound
            else:
                role = roles[0]
        except NoResultFound:
            raise ValueError("Role not found")
        return role

    def __str__(self):
        return f"name='{self.name}', description='{self.description}', uuid='{self.uuid}', is_active='{self.is_active}'"

    # @classmethod
    # async def remove_user_from_role(
    #     cls, db: AsyncSession, user_id: int, role_id: int
    # ) -> None:
    #     try:
    #         try:
    #             user = await User.get(db, user_id)
    #             if not user:
    #                 raise NoResultFound
    #         except NoResultFound:
    #             raise ValueError("User not found")

    #         try:
    #             role = await Role.get(db, role_id)
    #             if not role:
    #                 raise NoResultFound
    #         except NoResultFound:
    #             raise ValueError("Role not found")

    #         # try:
    #         #     project = await Project.get(db, project_id)
    #         #     if not project:
    #         #         raise NoResultFound
    #         # except NoResultFound:
    #         #     raise ValueError("Project not found")

    #         try:
    #             user.roles.remove(role)
    #         except ValueError:
    #             raise ValueError("User - Role association does not exist")

    #         try:
    #             await db.commit()
    #         except IntegrityError:
    #             await db.rollback()
    #             raise ValueError("User - Role association does not exist")
    #     except Exception:
    #         raise
    #     return {"detail": "User removed from role"}


# class ProjectRole(BaseEntity):
#     __tablename__ = "project_roles"
#     __table_params__ = (UniqueConstraint("name", "project_id"),)
#     name: Mapped[str] = mapped_column(String, unique=False, nullable=False)
#     description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     project_id: Mapped[int] = mapped_column(
#         Integer, ForeignKey("projects.id"), nullable=False
#     )
#     is_active: Mapped[bool] = mapped_column(Boolean, default=True)
#     projects: Mapped[List["Project"]] = relationship(
#         back_populates="project_roles",
#         lazy="selectin",
#     )
#     users: Mapped[List["User"]] = relationship(
#         secondary=UserProjectRole.__table__,
#         back_populates="project_roles",
#         lazy="selectin",
#     )

#     def __repr__(self):
#         return f"<ProjectRole {self.id}: title={self.name}>"

#     @classmethod
#     async def get(cls, db: AsyncSession, id: int) -> "ProjectRole":
#         role = (await db.execute(select(cls).where(cls.id == id))).scalars().first()
#         if not role:
#             raise ValueError("Role not found")
#         return role

#     @classmethod
#     async def get_all(cls, db: AsyncSession) -> Sequence["ProjectRole"]:
#         roles = (await db.execute(select(cls))).scalars().all()
#         return roles

#     @classmethod
#     async def create(
#         cls,
#         db: AsyncSession,
#         user_id: int,
#         name: str,
#         project_id: int,
#         description: str | None = None,
#         is_active: bool = True,
#     ) -> "ProjectRole":
#         project_role = cls(
#             name=name,
#             description=description,
#             project_id=project_id,
#             is_active=is_active,
#             uuid=str(uuid4()),
#             created_by=user_id,
#             updated_by=user_id,
#         )
#         db.add(project_role)
#         try:
#             await db.commit()
#             await db.refresh(project_role)
#         except IntegrityError:
#             await db.rollback()
#             raise ValueError(
#                 "Project role with that name already exists for the project"
#             )
#         return project_role
