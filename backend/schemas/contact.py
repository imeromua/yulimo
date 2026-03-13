"""Pydantic-схема для форми зворотного зв'язку."""

from pydantic import BaseModel, EmailStr, Field


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    message: str = Field(..., min_length=5, max_length=2000)
