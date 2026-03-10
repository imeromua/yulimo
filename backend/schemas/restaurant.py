"""Pydantic-схеми для ресторану."""

from datetime import date, time
from typing import Optional

from pydantic import BaseModel, Field


class TableReservationCreate(BaseModel):
    guest_name: str = Field(..., min_length=2, max_length=100)
    guest_phone: str = Field(..., min_length=7, max_length=20)
    date: date
    time: time
    guests_count: int = Field(..., ge=1, le=50)
    comment: Optional[str] = Field(None, max_length=500)


class TableReservationResponse(BaseModel):
    id: int
    guest_name: str
    guest_phone: str
    date: date
    time: time
    guests_count: int
    status: str

    model_config = {"from_attributes": True}
