"""Адміністративні маршрути (захищені JWT + роллю admin)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import require_admin
from models.booking import BookingStatus
from models.user import User
from services.booking_service import (
    BookingNotFoundError,
    BookingConflictError,
    RoomNotFoundError,
    get_all_bookings,
    update_booking_status,
)
from services.restaurant_service import get_all_table_reservations

router = APIRouter()


@router.get("/bookings")
def get_all_bookings_endpoint(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Усі бронювання (тільки для адміністраторів)."""
    return get_all_bookings(db)


@router.patch("/bookings/{booking_id}/status")
def update_booking_status_endpoint(
    booking_id: int,
    status: BookingStatus,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Оновити статус бронювання (тільки для адміністраторів)."""
    try:
        update_booking_status(booking_id, status, db)
    except BookingNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return {"success": True}


@router.get("/table-reservations")
def get_table_reservations_endpoint(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Усі резервації столиків (тільки для адміністраторів)."""
    return get_all_table_reservations(db)

