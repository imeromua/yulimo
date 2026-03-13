from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ContentBlockRead(BaseModel):
    key: str
    label: str
    value: str
    block_type: str
    section: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class ContentBlockCreate(BaseModel):
    key: str
    label: str
    value: str = ""
    block_type: str = "text"
    section: str = "other"


class ContentBlockUpdate(BaseModel):
    value: str
