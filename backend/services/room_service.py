"""Сервіс номерів."""

from sqlalchemy.orm import Session

from models.room import Room
from schemas.room import RoomCreate


class RoomNotFoundError(Exception):
    pass


def get_active_rooms(db: Session) -> list[Room]:
    """Повертає список активних номерів."""
    return db.query(Room).filter(Room.is_active == True).all()


def get_room_by_id(room_id: int, db: Session) -> Room:
    """Повертає номер за ID або кидає RoomNotFoundError."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise RoomNotFoundError("Номер не знайдено")
    return room


def create_room(data: RoomCreate, db: Session) -> Room:
    """Створює новий номер."""
    room = Room(**data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room
