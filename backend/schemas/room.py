"""Pydantic-схеми для номерів."""

from typing import List, Optional

from pydantic import BaseModel, Field


class RoomBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., max_length=50)
    description: Optional[str] = None
    capacity: int = Field(default=2, ge=1, le=50)
    area: Optional[float] = Field(None, gt=0)
    price: float = Field(..., gt=0)
    amenities: List[str] = []
    photos: List[str] = []
    is_active: bool = True


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    capacity: Optional[int] = Field(None, ge=1, le=50)
    area: Optional[float] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    amenities: Optional[List[str]] = None
    photos: Optional[List[str]] = None
    is_active: Optional[bool] = None


class RoomResponse(RoomBase):
    id: int

    model_config = {"from_attributes": True}

