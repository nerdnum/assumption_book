from typing import Optional

from fastapi_camelcase import CamelModel


class RoleBase(CamelModel):
    name: str | None = None
    description: str | None = None
    is_active: Optional[bool] = True
    is_system_role: Optional[bool] = False


class RoleUpdate(RoleBase):
    pass


class RoleCreate(RoleBase):
    name: str


class Role(RoleBase):
    id: int
    uuid: str

    class Config:
        from_attributes = True


class SimpleRole(CamelModel):
    id: int
    name: str


# class RoleWithUsers(Role):
#     users: list["User"] = []


# class UserRoleCreate(UserRoleBase):
#     pass


# class UserRole(UserRoleBase):
#     id: int
#     uuid: str

#     class Config:
#         from_attributes = True


# class UserRoleInUpdate(UserRoleBase):
#     user_id: Optional[int] = None
#     role_id: Optional[int] = None
#     project_id: Optional[int] = None
