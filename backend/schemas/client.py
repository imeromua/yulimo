from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class ClientCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    birthday: Optional[date] = None
    notes: Optional[str] = None
    source: Optional[str] = None  # website | phone | referral


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    birthday: Optional[date] = None
    notes: Optional[str] = None
    source: Optional[str] = None
    is_active: Optional[bool] = None


class ClientRead(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[str] = None
    birthday: Optional[date] = None
    notes: Optional[str] = None
    source: Optional[str] = None
    is_active: bool
    bookings_count: int = 0
    last_visit: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
