# Standard libary imports
from typing import List, Optional
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
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

# App imports
from app.services.database import BaseEntity


class UserProject(BaseEntity):
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
        return f"<UserProject {self.user_id}, {self.project_id}>"


class ProjectRole(BaseEntity):
    __tablename__ = "project_roles"
    __table_args__ = (UniqueConstraint("project_id", "role_id"),)

    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id"), nullable=False
    )


class UserRole(BaseEntity):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", "project_id"),)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id"), nullable=False
    )
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=True
    )

    def __repr__(self):
        return f"<UserRole {self.user_id}, {self.role_id}, {self.project_id}>"

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        user_id: int,
        role_id: int,
        project_id: int,
        current_user_id: int,
        uuid: str = str(uuid4()),
    ) -> "UserRole":
        try:
            user = await User.get(db, user_id)
            if not user:
                raise ValueError("User not found")

            project = None
            if project_id:
                project = await Project.get_project_by_id(db, project_id)
                if project is None:
                    raise ValueError("Project not found")

                if project not in user.projects:
                    raise ValueError("This user is not associated with this project")

                role = await Role.get(db, role_id)
                if role is None:
                    raise ValueError("Role not found")

                ## Remember the project existsm, it is tested first
                if role.is_system_role:
                    raise ValueError("Cannot assign a system role to project")
                else:
                    if role not in project.roles:
                        raise ValueError(
                            "This role is not associated with this project"
                        )

            user_project_role = cls(
                user_id=user_id,
                role_id=role_id,
                project_id=project_id,
                uuid=uuid,
                created_by=current_user_id,
                updated_by=current_user_id,
            )
            db.add(user_project_role)
            await db.commit()
            await db.refresh(user_project_role)
        except IntegrityError:
            await db.rollback()
            raise ValueError("User -> Project -> Role association already exists")
        except Exception:
            raise
        return user_project_role

    @classmethod
    async def get_user_roles(cls, db: AsyncSession, user_id: int) -> "UserRole":
        try:
            user = await User.get(db, user_id)
            if not user:
                raise ValueError("User not found")

            user_roles = (
                (await db.execute(select(cls).where(cls.user_id == user_id)))
                .scalars()
                .all()
            )
        except Exception as error:
            raise error
        return user_roles


###--------------------- Project ---------------------###


class User(BaseEntity):
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
    )
    roles: Mapped[List["Role"]] = relationship(
        secondary=UserRole.__table__, lazy="selectin", back_populates="users"
    )

    def __repr__(self):
        return f"<User {self.id}: username={self.username}, email={self.email}>"

    @classmethod
    async def get_all(cls, db: AsyncSession) -> list["User"]:
        users = (await db.execute(select(cls))).scalars().all()
        return users

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        full_name: str,
        username: str | None,
        preferred_name: str | None,
        email: str,
        user_id: int,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> "User":
        print(
            "create",
            username,
            full_name,
            preferred_name,
            email,
            is_active,
            is_superuser,
            user_id,
        )
        user = cls(
            full_name=full_name,
            username=username,
            preferred_name=preferred_name,
            email=email,
            is_active=is_active,
            is_superuser=is_superuser,
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

    @classmethod
    async def get(cls, db: AsyncSession, id: int) -> "User":
        try:
            user = await db.get(cls, id)
            if not user:
                raise NoResultFound
        except NoResultFound:
            raise ValueError("User not found")
        return user

    @classmethod
    async def get_user_project_roles(cls, db: AsyncSession, id: int) -> "User":
        try:
            user = await db.get(cls, id)
            if not user:
                raise ValueError("User not found")

            user_project_roles = await UserRole.get_user_roles(db, id)
            role_definitions = []
            for role in user_project_roles:
                role_definitions.append((role.user_id, role.role_id, role.project_id))

            if user.projects:
                for project in user.projects:
                    possible_roles = project.roles
                    project.roles = []
                    for role in possible_roles:
                        role_definition = (id, role.id, project.id)
                        if role_definition in role_definitions:
                            project.roles.append(role)

        except Exception as error:
            raise error

        return user

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        id: int,
        full_name: str | None,
        username: str | None,
        preferred_name: str | None,
        email: str | None,
        is_active: bool | None,
        is_superuser: bool | None,
        user_id: int,
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
        except Exception:
            await db.rollback()
            raise
        return user

    @classmethod
    async def set_password(
        cls, db: AsyncSession, id: int, hashed_password: str | None, user_id: int
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
    async def activate(cls, db: AsyncSession, id: int, user_id: int) -> "User":
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
    async def deactivate(cls, db: AsyncSession, id: int, user_id: int) -> "User":
        try:
            print("deactivate", id, user_id)
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
    users: Mapped[List[User]] = relationship(
        secondary=UserProject.__table__,
        lazy="selectin",
        back_populates="projects",
    )
    roles: Mapped[List["Role"]] = relationship(
        secondary=ProjectRole.__table__,
        lazy="selectin",
        back_populates="projects",
    )

    def __repr__(self):
        return f"<Project {self.id}: title={self.title}>"

    @classmethod
    async def get_all(cls, db: AsyncSession) -> list["Project"]:
        projects = (await db.execute(select(cls))).scalars().all()
        return projects

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        title: str,
        description: str | None,
        project_manager: str | None,
        logo_url: str | None,
        user_id: int,
    ) -> "Project":

        project = cls(
            title=title,
            description=description,
            project_manager=project_manager,
            logo_url=logo_url,
            uuid=str(uuid4()),
            created_by=user_id,
            updated_by=user_id,
        )

        try:
            db.add(project)
            await db.commit()
            await db.refresh(project)
        except IntegrityError as error:
            await db.rollback()
            raise error
            # raise ValueError("Project with this title already exists")
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
        id: int,
        title: str | None,
        description: str | None,
        project_manager: str | None,
        logo_url: str | None,
        user_id: int,
    ) -> "Project":
        try:
            project = await db.get(cls, id)
            if title is not None:
                project.title = title
            if description is not None:
                project.description = description
            if logo_url is not None:
                project.logo_url = logo_url
            if project_manager is not None:
                project.project_manager = project_manager
            project.updated_by = user_id
            try:
                await db.commit()
                await db.refresh(project)
            except IntegrityError:
                await db.rollback()
                raise ValueError("Project with this title already exists")
        except NoResultFound:
            raise ValueError("Project not found")
        return project

    @classmethod
    async def update_by_id(
        cls,
        db: AsyncSession,
        id: int,
        title: str | None,
        description: str | None,
        project_manager: str | None,
        logo_url: str | None,
        user_id: int,
    ) -> "Project":
        return await cls.update_project(
            db, id, title, description, project_manager, logo_url, user_id
        )

    @classmethod
    async def delete_by_id(cls, db: AsyncSession, id: int) -> None:
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
        cls, db: AsyncSession, project_id: int, role_id: int
    ) -> "Project":
        try:
            project = await cls.get_project_by_id(db, project_id)
            if project is None:
                raise ValueError("Project not found")
            role = await Role.get(db, role_id)
            if role is None:
                raise ValueError("Role not found")
            if role.is_system_role:
                raise ValueError("Cannot assign a system role to project")
            project.roles.append(role)
            await db.commit()
            await db.refresh(project)
        except Exception as error:
            raise error
        return role


###--------------------- Role ---------------------###


class Role(BaseEntity):
    __tablename__ = "roles"
    name: str = Column(String, unique=True, nullable=False)
    description: str = Column(String, nullable=True)
    is_active: bool = Column(Boolean, default=True)
    is_system_role: bool = Column(Boolean, default=False)
    projects: Mapped[List["Project"]] = relationship(
        secondary=ProjectRole.__table__,
        back_populates="roles",
        lazy="selectin",
    )
    users: Mapped[List["User"]] = relationship(
        secondary=UserRole.__table__,
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self):
        return (
            f"<Role {self.id}: title={self.name}, is_system_role={self.is_system_role}>"
        )

    @classmethod
    async def get_all(cls, db: AsyncSession) -> list["Role"]:
        roles = (await db.execute(select(cls))).scalars().all()
        return roles

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        name: str,
        description: str,
        is_system_role: bool = False,
        is_active: bool = True,
    ) -> "Role":
        role = cls(
            name=name,
            description=description,
            is_system_role=is_system_role,
            is_active=is_active,
            uuid=str(uuid4()),
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
        id: int,
        name: str | None,
        description: str | None,
        is_system_role: bool | None,
    ) -> "Role":
        try:
            role = await cls.get(db, id)
            if name:
                role.name = name
            if description:
                role.description = description
            if is_system_role:
                role.is_system_role = is_system_role
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

    @classmethod
    async def remove_user_from_role(
        cls, db: AsyncSession, user_id: int, role_id: int
    ) -> None:
        try:
            try:
                user = await User.get(db, user_id)
                if not user:
                    raise NoResultFound
            except NoResultFound:
                raise ValueError("User not found")

            try:
                role = await Role.get(db, role_id)
                if not role:
                    raise NoResultFound
            except NoResultFound:
                raise ValueError("Role not found")

            # try:
            #     project = await Project.get(db, project_id)
            #     if not project:
            #         raise NoResultFound
            # except NoResultFound:
            #     raise ValueError("Project not found")

            try:
                user.roles.remove(role)
            except ValueError:
                raise ValueError("User - Role association does not exist")

            try:
                await db.commit()
            except IntegrityError:
                await db.rollback()
                raise ValueError("User - Role association does not exist")
        except Exception:
            raise
        return {"detail": "User removed from role"}
