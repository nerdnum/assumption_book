from pydantic import BaseModel
from typing import Optional
from fastapi_camelcase import CamelModel


class ProjectBase(CamelModel):
    title: str
    description: str | None = None
    slug: str | None = None
    project_manager: str | None = None
    logo_url: str | None = None


class ProjectUpdate(CamelModel):
    title: Optional[str] = None
    slug: Optional[str] = None
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
