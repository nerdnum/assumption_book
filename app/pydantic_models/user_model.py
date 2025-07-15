from typing import Optional
from datetime import datetime

from fastapi_camelcase import CamelModel
from pydantic import EmailStr

from app.pydantic_models.project_model import (
    Project,
    ProjectMinimalInfo,
    ProjectBasicInfo,
    ProjectWithProjectRoles,
)
from app.pydantic_models.role_model import SimpleRole


class UserBase(CamelModel):
    full_name: str | None = None
    preferred_name: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None
    is_superuser: bool | None = False

    class Config:
        from_attributes = True


class UserUpdate(UserBase):
    pass
    system_roles: list[SimpleRole] = []


class UserCreate(UserBase):
    full_name: str
    preferred_name: str
    email: EmailStr
    is_active: Optional[bool] = True
    system_roles: list[SimpleRole] = []


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
    system_roles: list[SimpleRole] = []


class UserInDB(User):
    password: str
    is_active: bool = True


class UserWithProjectRoles(User):
    project_roles: list["SimpleRole"] = []


class UserWithSystemRoles(User):
    system_roles: list["SimpleRole"] = []


class UserWithProjectsAndSystemRoles(User):
    projects: list["ProjectWithProjectRoles"] = []
    system_roles: list["SimpleRole"] = []

    class Config:
        from_attributes = True
