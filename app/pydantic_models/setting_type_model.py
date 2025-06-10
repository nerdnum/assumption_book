from typing import Any, Optional

from fastapi_camelcase import CamelModel
from pydantic import model_validator


class SettingTypeBase(CamelModel):
    title: str | None = None
    description: str | None = None
    default_text: str | None = None


class SettingTypeUpdate(SettingTypeBase):

    @model_validator(mode="before")
    @classmethod
    def check_at_least_one_value(cls, data: dict) -> Any:
        if not any(
            # for the before validator, the json keys are not converted to kebabcase yet,
            # it is still in camelCase, so you have to specificy camelCase for testing
            [data.get("title"), data.get("description"), data.get("defaultText")]
        ):
            raise ValueError(
                "At least one of title, description or default_text must be provided"
            )
        return data


class SettingTypeCreate(SettingTypeBase):
    title: str


class SettingType(SettingTypeBase):
    id: int
    uuid: str

    class Config:
        from_attributes = True
