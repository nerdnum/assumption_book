from typing import Optional
from datetime import datetime

from fastapi_camelcase import CamelModel
from pydantic import EmailStr

from app.pydantic_models.project_model import (
    Project,
    ProjectWithRoles,
    ProjectBasicInfo,
)
from app.pydantic_models.role_model import Role


class UserBase(CamelModel):
    full_name: str
    username: Optional[str] = None
    preferred_name: Optional[str] = None
    email: EmailStr
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

    class Config:
        from_attributes = True


class UserUpdate(UserBase):
    full_name: Optional[str] = None
    username: Optional[str] = None
    preferred_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    uuid: str
    is_active: Optional[bool] = True
    is_first_login: Optional[bool] = True
    is_superuser: Optional[bool] = False


class FullUser(User):
    is_active: Optional[bool] = True
    is_first_login: Optional[bool] = True
    is_superuser: Optional[bool] = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None


class UserInDB(User):
    password: str
    is_active: bool = True


class UserWithProjects(User):
    projects: list["ProjectBasicInfo"] = []


class ProjectWithUsers(Project):
    users: list[User] = []


class UserWithRoles(User):
    roles: list["Role"] = []


class UserWithProjectRoles(User):
    projects: list["ProjectWithRoles"] = []
