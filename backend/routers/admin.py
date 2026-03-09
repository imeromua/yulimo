from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.booking import Booking, BookingStatus
from models.restaurant import TableReservation

router = APIRouter()


@router.get("/bookings")
def get_all_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).order_by(Booking.created_at.desc()).all()


@router.patch("/bookings/{booking_id}/status")
def update_booking_status(
    booking_id: int,
    status: BookingStatus,
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронювання не знайдено")
    booking.status = status
    db.commit()
    return {"success": True}


@router.get("/table-reservations")
def get_table_reservations(db: Session = Depends(get_db)):
    return db.query(TableReservation).order_by(TableReservation.created_at.desc()).all()
