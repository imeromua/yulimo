from pydantic import BaseModel
from typing import List, Optional


class RoomBase(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    capacity: int = 2
    area: Optional[float] = None
    price: float
    amenities: List[str] = []
    photos: List[str] = []
    is_active: bool = True


class RoomCreate(RoomBase):
    pass


class RoomResponse(RoomBase):
    id: int

    class Config:
        from_attributes = True
