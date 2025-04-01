from typing import Optional

from fastapi_camelcase import CamelModel

from app.pydantic_models.role_model import Role


class ProjectBase(CamelModel):
    title: str
    description: str | None = None
    project_manager: str | None = None
    logo_url: str | None = None


class ProjectBasicInfo(CamelModel):
    id: int
    title: str
    description: str | None = None


class ProjectUpdate(CamelModel):
    title: Optional[str] = None
    description: Optional[str] = None
    project_manager: Optional[str] = None
    logo_url: Optional[str] = None


# TODO - Add pydantic validation and error checking for the class


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    uuid: str

    class Config:
        from_attributes = True


class ProjectWithRoles(Project):
    roles: list["Role"] = []


class RoleWithProjects(Role):
    projects: list["Project"] = []


class CompSpec(CamelModel):
    id: int


class DocSpec(CamelModel):
    type: str
    project_id: int
    components: list[CompSpec]

    class Config:
        from_attributes = True


class DocResponse(CamelModel):
    status: str
    name: str
    url: str
