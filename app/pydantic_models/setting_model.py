from typing import Any, List, Optional

from fastapi_camelcase import CamelModel


class SettingBase(CamelModel):
    title: str
    description: str | None = None
    value: Optional[Any]
    setting_type_id: int


class SettingUpdate(SettingBase):
    title: Optional[str] = None
    description: Optional[str] = None
    value: Optional[Any] = None
    setting_type_id: Optional[int] = None


class SettingCreate(SettingBase):
    pass


class Setting(SettingBase):
    id: int
    uuid: str

    class Config:
        from_attributes = True
