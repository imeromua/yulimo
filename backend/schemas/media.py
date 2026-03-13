from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MediaCreate(BaseModel):
    original_name: str
    section: str = "other"
    title_uk: Optional[str] = None
    sort_order: int = 0


class MediaUpdate(BaseModel):
    title_uk: Optional[str] = None
    section: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class MediaRead(BaseModel):
    id: int
    filename: str
    original_name: str
    section: str
    title_uk: Optional[str] = None
    sort_order: int
    is_active: bool
    uploaded_at: datetime

    model_config = {"from_attributes": True}
