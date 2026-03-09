from pydantic import BaseModel
from typing import Optional
from datetime import date


class BookingCreate(BaseModel):
    room_id: int
    guest_name: str
    guest_phone: str
    guest_email: Optional[str] = None
    check_in: date
    check_out: date
    guests_count: int = 1
    comment: Optional[str] = None


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

    class Config:
        from_attributes = True
