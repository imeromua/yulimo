from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class SiteSettingRead(BaseModel):
    id: int
    key: str
    value: str
    label: str
    group: str
    setting_type: str

    model_config = {"from_attributes": True}


class SiteSettingUpdate(BaseModel):
    value: str


class SiteSettingBulkUpdate(BaseModel):
    settings: dict  # {key: value, ...}
