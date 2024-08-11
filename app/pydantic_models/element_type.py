from pydantic import BaseModel, model_validator
from pydantic_core import PydanticCustomError
from typing import Optional, Any
from typing_extensions import Self


class ElementTypeBase(BaseModel):
    title: str
    description: str | None = None
    default_text: str | None = None


class ElementTypeUpdate(ElementTypeBase):
    title: Optional[str] = None
    description: Optional[str] = None
    default_text: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def check_at_least_one_value(cls, data: dict) -> Any:
        if not any([data.get('title'), data.get('description'), data.get('default_text')]):
            raise ValueError(
                'At least one of title, description or default_text must be provided')
        return data


class ElementTypeCreate(ElementTypeBase):
    pass


class ElementType(ElementTypeBase):
    id: int
    uuid: str

    class Config:
        from_attributes = True
