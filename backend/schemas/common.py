"""Спільні Pydantic-схеми для стандартних відповідей API."""

from typing import Any, Optional

from pydantic import BaseModel


class StandardResponse(BaseModel):
    """Стандартна обгортка відповіді."""

    success: bool
    data: Any = None
    message: str = ""


class ErrorResponse(BaseModel):
    """Стандартна обгортка відповіді з помилкою."""

    success: bool = False
    error: str
    details: Any = None
