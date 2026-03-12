"""Pydantic-схеми для ресторану."""

import enum
from datetime import date, time
from typing import Optional

from pydantic import BaseModel, Field


class MenuCategory(str, enum.Enum):
    starters = "starters"
    soups    = "soups"
    mains    = "mains"
    grill    = "grill"
    desserts = "desserts"
    drinks   = "drinks"


class MenuItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: MenuCategory
    price: float = Field(..., gt=0)
    description: Optional[str] = None
    weight: Optional[str] = Field(None, max_length=20)
    photo: Optional[str] = Field(None, max_length=255)
    is_active: bool = True


class MenuItemResponse(BaseModel):
    id: int
    name: str
    category: str
    price: float
    description: Optional[str] = None
    weight: Optional[str] = None
    photo: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


class TableReservationCreate(BaseModel):
    guest_name: str = Field(..., min_length=2, max_length=100)
    guest_phone: str = Field(..., min_length=7, max_length=20)
    guest_email: Optional[str] = Field(None, max_length=100)
    date: date
    time: time
    guests_count: int = Field(..., ge=1, le=50)
    comment: Optional[str] = Field(None, max_length=500)


class TableReservationResponse(BaseModel):
    id: int
    guest_name: str
    guest_phone: str
    guest_email: Optional[str] = None
    date: date
    time: time
    guests_count: int
    status: str

    model_config = {"from_attributes": True}
