from pydantic import BaseModel
from typing import Optional


class ElementBase(BaseModel):
    title: str
    description: str | None = None
    project_id: int
    element_type_id: int


class ElementUpdate(ElementBase):
    title: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[int] = None
    element_type_id: Optional[int] = None


class ElementCreate(ElementBase):
    pass


class Element(ElementBase):
    id: int
    uuid: str

    class Config:
        from_attributes = True
