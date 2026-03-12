"""Маршрути для бронювань."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.room import Room
from schemas.booking import BookingCreate, BookingResponse
from services.booking_service import (
    BookingConflictError,
    RoomNotFoundError,
    check_availability,
    create_booking,
)
from services import email_service

router = APIRouter()


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking_endpoint(data: BookingCreate, db: Session = Depends(get_db)):
    """Створити нове бронювання з перевіркою доступності."""
    try:
        booking = create_booking(data, db)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except BookingConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    room = db.query(Room).filter(Room.id == booking.room_id).first()
    room_name = room.name if room else ""

    await email_service.send_booking_confirmation(booking, room_name)
    await email_service.send_booking_notification_admin(booking, room_name)

    return booking


@router.get("/check-availability")
def check_availability_endpoint(
    room_id: int,
    check_in: date,
    check_out: date,
    db: Session = Depends(get_db),
):
    """Перевірити доступність номеру на задані дати."""
    if check_out <= check_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дата виїзду має бути пізніше дати заїзду",
        )
    available = check_availability(db, room_id, check_in, check_out)
    return {"available": available}

