from pydantic import BaseModel
from typing import Optional
from pydantic import EmailStr
from pydantic.types import UUID4
from fastapi_camelcase import CamelModel


class UserBase(CamelModel):
    username: str
    email: EmailStr
    full_name: str


class UserUpdate(UserBase):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    uuid: str

    class Config:
        from_attributes = True


class UserInDB(User):
    password: str
    disabled: bool = True


class RoleBase(BaseModel):
    name: str
    description: str | None = None


class RoleUpdate(RoleBase):
    name: Optional[str] = None
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int
    uuid: str

    class Config:
        from_attributes = True


class RoleInDB(Role):
    disabled: bool = True


class RoleWithUsers(Role):
    users: list["User"] = []


class UserWithRoles(User):
    roles: list["Role"] = []
