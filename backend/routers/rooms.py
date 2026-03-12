"""Маршрути для роботи з номерами."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from dependencies.auth import require_admin
from models.user import User
from schemas.room import RoomCreate, RoomResponse, RoomUpdate
from services.room_service import RoomNotFoundError, create_room, get_active_rooms, get_room_by_id, update_room

router = APIRouter()


@router.get("/", response_model=List[RoomResponse])
def get_rooms(db: Session = Depends(get_db)):
    """Список активних номерів."""
    return get_active_rooms(db)


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    """Деталі конкретного номеру."""
    try:
        return get_room_by_id(room_id, db)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room_endpoint(
    room: RoomCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Створити новий номер (тільки для адміністраторів)."""
    return create_room(room, db)


@router.patch("/{room_id}", response_model=RoomResponse)
def update_room_endpoint(
    room_id: int,
    room: RoomUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Оновити існуючий номер (тільки для адміністраторів)."""
    try:
        return update_room(room_id, room, db)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

