"""Стандартизовані відповіді API."""

from typing import Any, Optional


def success_response(data: Any = None, message: str = "") -> dict:
    """Формує відповідь про успіх."""
    return {"success": True, "data": data, "message": message}


def error_response(error: str, details: Any = None) -> dict:
    """Формує відповідь про помилку."""
    return {"success": False, "error": error, "details": details or {}}
