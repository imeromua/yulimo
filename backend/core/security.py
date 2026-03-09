"""Утиліти безпеки: хешування паролів та JWT-токени."""

import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from core.config import settings


# ---------------------------------------------------------------------------
# Хешування паролів
# ---------------------------------------------------------------------------


def hash_password(plain: str) -> str:
    """Повертає bcrypt-хеш відкритого тексту пароля."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Перевіряє збіг відкритого тексту з bcrypt-хешем."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ---------------------------------------------------------------------------
# JWT-токени
# ---------------------------------------------------------------------------


def _create_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str, role: str = "admin") -> str:
    """Генерує короткоживучий access-токен."""
    return _create_token(
        {"sub": subject, "role": role, "type": "access"},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: str) -> str:
    """Генерує довгоживучий refresh-токен."""
    return _create_token(
        {"sub": subject, "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> Optional[dict]:
    """Розкодовує токен. Повертає payload або None у разі помилки."""
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        return None
