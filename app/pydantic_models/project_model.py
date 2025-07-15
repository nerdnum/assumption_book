from typing import Optional

from fastapi_camelcase import CamelModel

from app.pydantic_models.role_model import Role


class ProjectBase(CamelModel):
    title: str | None
    description: str | None = None
    project_manager: str | None = None
    logo_url: str | None = None
    image_url: str | None = None


class ProjectUpdate(ProjectBase):
    title: str | None = None


# TODO - Add pydantic validation and error checking for the class


class ProjectCreate(ProjectBase):
    title: str


class Project(ProjectBase):
    id: int
    uuid: str

    class Config:
        from_attributes = True


class ProjectBasicInfo(CamelModel):
    id: int
    uuid: str
    title: str
    image_url: str | None = None
    logo_url: str | None = None
    description: str | None = None


class ProjectMinimalInfo(CamelModel):
    id: int
    uuid: str
    title: str


class ProjectWithProjectRoles(ProjectBasicInfo):
    project_roles: list["Role"] = []


class RoleWithProjects(Role):
    projects: list["Project"] = []


class CompSpec(CamelModel):
    id: int


class DocSpec(CamelModel):
    type: str
    project_id: int
    document_type: str
    components: list[CompSpec]

    class Config:
        from_attributes = True


class DocResponse(CamelModel):
    status: str
    name: str
    url: str

    class Config:
        from_attributes = True


class RoleRequest(CamelModel):
    project_id: int
    role_id: int

    class Config:
        from_attributes = True
