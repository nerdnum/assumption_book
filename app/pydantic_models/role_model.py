from typing import Optional

from fastapi_camelcase import CamelModel


class RoleBase(CamelModel):
    name: str
    description: str | None = None
    is_system_role: Optional[bool] = False


class RoleUpdate(RoleBase):
    name: Optional[str] = None
    description: Optional[str] = None
    is_system_role: Optional[bool] = None


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int
    uuid: str

    class Config:
        from_attributes = True


class RoleInDB(Role):
    is_active: bool = True


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
