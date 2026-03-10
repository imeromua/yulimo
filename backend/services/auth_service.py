"""Сервіс автентифікації: реєстрація, логін, refresh."""

from sqlalchemy.orm import Session

from core.logging_config import auth_logger
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from models.user import User


class AuthenticationError(Exception):
    pass


class RegistrationError(Exception):
    pass


class TokenError(Exception):
    pass


def register_user(email: str, password: str, name: str | None, db: Session) -> User:
    """Реєструє нового користувача. Кидає RegistrationError якщо email вже існує."""
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise RegistrationError("Користувач з таким email вже існує")

    user = User(
        email=email,
        password=hash_password(password),
        name=name,
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    auth_logger.info("Зареєстровано нового користувача: %s", email)
    return user


def authenticate_user(email: str, password: str, db: Session) -> tuple[str, str]:
    """Автентифікує користувача, повертає (access_token, refresh_token).
    Кидає AuthenticationError при невірних облікових даних."""
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user or not verify_password(password, user.password):
        auth_logger.warning("Невдала спроба входу для: %s", email)
        raise AuthenticationError("Невірний email або пароль")

    access_token = create_access_token(user.email, user.role)
    refresh_token = create_refresh_token(user.email)
    auth_logger.info("Успішний вхід: %s", email)
    return access_token, refresh_token


def refresh_access_token(refresh_token: str, db: Session) -> str:
    """Оновлює access-токен за допомогою refresh-токена."""
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise TokenError("Недійсний або прострочений refresh-токен")

    email: str = payload.get("sub", "")
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user:
        raise TokenError("Користувача не знайдено")

    return create_access_token(user.email, user.role)
