"""Адміністративні маршрути (захищені JWT + роллю admin)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import require_admin
from models.booking import BookingStatus
from models.room import Room
from models.user import User
from services.booking_service import (
    BookingNotFoundError,
    get_all_bookings,
    update_booking_status,
)
from services.restaurant_service import get_all_table_reservations
from services.restaurant_service import get_all_menu_items
from services import email_service

router = APIRouter()


@router.get("/bookings")
def get_all_bookings_endpoint(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Усі бронювання (тільки для адміністраторів)."""
    return get_all_bookings(db)


@router.patch("/bookings/{booking_id}/status")
async def update_booking_status_endpoint(
    booking_id: int,
    new_status: BookingStatus = Query(..., alias="status"),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Оновити статус бронювання (тільки для адміністраторів)."""
    try:
        booking = update_booking_status(booking_id, new_status, db)
    except BookingNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    room = db.query(Room).filter(Room.id == booking.room_id).first()
    room_name = room.name if room else ""

    await email_service.send_booking_status_update(booking, new_status, room_name)

    return {"success": True}


@router.get("/table-reservations")
def get_table_reservations_endpoint(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Усі резервації столиків (тільки для адміністраторів)."""
    return get_all_table_reservations(db)


@router.get("/menu")
def get_admin_menu_endpoint(
    category: str = "",
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Усі позиції меню включно з неактивними (тільки для адміністраторів)."""
    return get_all_menu_items(db, category or None)

