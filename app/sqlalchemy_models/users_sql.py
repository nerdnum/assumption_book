# Standard libary imports
from sqlalchemy import Column, String, Boolean, select, Table, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from uuid import uuid4
from typing import Optional, List
from sqlalchemy_utc import UtcDateTime, utcnow


# App imports
from app.services.database import BaseEntity


association_table = Table(
    "user_role_association", BaseEntity.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role_id", Integer, ForeignKey("roles.id")),
    Column("created_at", UtcDateTime(timezone=True), nullable=False,
           server_default=utcnow()),
    Column("udpated_at", UtcDateTime(timezone=True), nullable=False,
           server_default=utcnow(), onupdate=utcnow()),
    UniqueConstraint("user_id", "role_id")
)


class User(BaseEntity):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[Optional[str]] = mapped_column(String)
    disabled: Mapped[bool] = mapped_column(Boolean, default=True)
    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary=lambda: association_table, back_populates="users", lazy="selectin")

    @classmethod
    async def get_all(cls, db: AsyncSession) -> list["User"]:
        users = (await db.execute(select(cls))).scalars().all()
        return users

    @classmethod
    async def create(cls, db: AsyncSession, username: str, full_name: str, email: str) -> "User":
        user = cls(username=username, full_name=full_name,
                   email=email, uuid=str(uuid4()))
        try:
            db.add(user)
            await db.commit()
            await db.refresh(user)
        except IntegrityError as error:
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
    async def update(cls, db: AsyncSession, id: int, username: str | None, full_name: str | None, email: str | None) -> "User":
        try:
            user = await cls.get(db, id)
            if username:
                user.username = username
            if full_name:
                user.full_name = full_name
            if email:
                user.email = email
            try:
                await db.commit()
                await db.refresh(user)
            except IntegrityError as error:
                await db.rollback()
                raise ValueError("User with that email already exists")
        except Exception:
            await db.rollback()
            raise
        return user

    @classmethod
    async def set_password(cls, db: AsyncSession, id: int, hashed_password: str | None) -> "User":
        try:
            user = await cls.get(db, id)
            if hashed_password:
                user.password = hashed_password
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
            user = (await db.execute(select(cls).where(cls.uuid == uuid))).scalars().first()
            if not user:
                raise NoResultFound
        except NoResultFound:
            raise ValueError("User not found")
        return user

    @classmethod
    async def get_user_by_username(cls, db: AsyncSession, username: str) -> "User":
        try:
            user = (await db.execute(select(cls).where(cls.username == username))).scalars().first()
            if not user:
                raise NoResultFound
        except NoResultFound:
            raise ValueError("User not found")
        return user

    @classmethod
    async def add_role(cls, db: AsyncSession, user_id: int, role_id: int) -> "User":
        try:
            try:
                user = await cls.get(db, user_id)
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

            user.roles.append(role)
            try:
                await db.commit()
                await db.refresh(user)
            except IntegrityError as error:
                await db.rollback()
                raise ValueError("User -> Role association already exists")
        except Exception:
            raise
        return user

    @classmethod
    async def activate(cls, db: AsyncSession, id: int) -> "User":
        try:
            user = await cls.get(db, id)
            user.disabled = False
            await db.commit()
            await db.refresh(user)
        except Exception:
            await db.rollback()
            raise
        return user

    @classmethod
    async def deactivate(cls, db: AsyncSession, id: int) -> "User":
        try:
            user = await cls.get(db, id)
            user.disabled = True
            await db.commit()
            await db.refresh(user)
        except Exception:
            await db.rollback()
            raise
        return user


class Role(BaseEntity):
    __tablename__ = "roles"
    name: str = Column(String, unique=True, nullable=False)
    description: str = Column(String, nullable=True)
    disabled: bool = Column(Boolean, default=True)
    users: Mapped[list["User"]] = relationship(
        "User", secondary=lambda: association_table, back_populates="roles", lazy="selectin")

    @classmethod
    async def get_all(cls, db: AsyncSession) -> list["Role"]:
        roles = (await db.execute(select(cls))).scalars().all()
        return roles

    @classmethod
    async def create(cls, db: AsyncSession, name: str, description: str) -> "Role":
        role = cls(name=name, description=description, uuid=str(uuid4()))
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
    async def update(cls, db: AsyncSession, id: int, name: str | None, description: str | None) -> "Role":
        try:
            role = await cls.get(db, id)
            if name:
                role.name = name
            if description:
                role.description = description
            try:
                await db.commit()
                await db.refresh(role)
            except IntegrityError as error:
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

    @ classmethod
    async def get_role_by_uuid(cls, db: AsyncSession, uuid: str) -> "Role":
        try:
            roles = (await db.execute(select(cls).where(cls.uuid == uuid))).scalars().all()
            if len(roles) == 0:
                raise NoResultFound
            else:
                role = roles[0]
        except NoResultFound:
            raise ValueError("Role not found")
        return role

    def __str__(self):
        return f"name='{self.name}', description='{self.description}', uuid='{self.uuid}', disabled='{self.disabled}'"

    @classmethod
    async def remove_user_from_role(cls, db: AsyncSession, user_id: int, role_id: int) -> None:
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

            try:
                user.roles.remove(role)
            except ValueError:
                raise ValueError("User - Role association does not exist")

            try:
                await db.commit()
            except IntegrityError as error:
                await db.rollback()
                raise ValueError("User - Role association does not exist")
        except Exception:
            raise
        return {"detail": "User removed from role"}
