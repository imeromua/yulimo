"""Pydantic-схеми для користувачів."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
