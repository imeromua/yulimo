"""Маршрути автентифікації: реєстрація, вхід, оновлення токена."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from services.auth_service import (
    AuthenticationError,
    RegistrationError,
    TokenError,
    authenticate_user,
    refresh_access_token,
    register_user,
)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Реєстрація нового адміністратора."""
    try:
        user = register_user(data.email, data.password, data.name, db)
    except RegistrationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    access_token, refresh_token = authenticate_user(data.email, data.password, db)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Вхід та отримання JWT-токенів."""
    try:
        access_token, refresh_token = authenticate_user(data.email, data.password, db)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    """Оновлення access-токена за допомогою refresh-токена."""
    try:
        access_token = refresh_access_token(data.refresh_token, db)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return TokenResponse(access_token=access_token, refresh_token=data.refresh_token)
