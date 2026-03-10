"""Pydantic-схеми для бронювань."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class BookingCreate(BaseModel):
    room_id: int
    guest_name: str = Field(..., min_length=2, max_length=100)
    guest_phone: str = Field(..., min_length=7, max_length=20)
    guest_email: Optional[str] = Field(None, max_length=100)
    check_in: date
    check_out: date
    guests_count: int = Field(default=1, ge=1, le=20)
    comment: Optional[str] = Field(None, max_length=500)

    @model_validator(mode="after")
    def check_dates(self) -> "BookingCreate":
        if self.check_out <= self.check_in:
            raise ValueError("Дата виїзду має бути пізніше дати заїзду")
        return self


class BookingResponse(BaseModel):
    id: int
    room_id: int
    guest_name: str
    guest_phone: str
    check_in: date
    check_out: date
    nights: int
    total_price: float
    status: str

    model_config = {"from_attributes": True}

