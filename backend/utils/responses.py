"""Стандартизовані відповіді API."""

from typing import Any


def success_response(data: Any = None, message: str = "") -> dict:
    """Формує відповідь про успіх."""
    return {"success": True, "data": data, "message": message}


def error_response(error: str, details: Any = None) -> dict:
    """Формує відповідь про помилку."""
    return {"success": False, "error": error, "details": details or {}}


def make_serializable_errors(errors: list) -> list:
    """Перетворює Pydantic validation errors у JSON-серіалізовний список.
    Конвертує ctx['error'] (ValueError та ін.) на рядки."""
    result = []
    for e in errors:
        err = dict(e)
        if "ctx" in err:
            err["ctx"] = {k: str(v) for k, v in err["ctx"].items()}
        result.append(err)
    return result
