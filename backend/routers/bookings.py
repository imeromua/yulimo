from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from database import get_db
from models.booking import Booking, BookingStatus
from models.room import Room
from schemas.booking import BookingCreate, BookingResponse

router = APIRouter()


@router.post("/", response_model=BookingResponse)
def create_booking(data: BookingCreate, db: Session = Depends(get_db)):
    # Перевіряємо номер
    room = db.query(Room).filter(Room.id == data.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Номер не знайдено")

    # Перевіряємо дати
    if data.check_out <= data.check_in:
        raise HTTPException(status_code=400, detail="Невірні дати")

    # Перевіряємо чи номер вільний
    conflict = db.query(Booking).filter(
        Booking.room_id == data.room_id,
        Booking.status != BookingStatus.cancelled,
        Booking.check_in < data.check_out,
        Booking.check_out > data.check_in
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="Номер зайнятий на ці дати")

    # Розраховуємо ціну
    nights = (data.check_out - data.check_in).days
    total_price = nights * room.price

    booking = Booking(
        **data.model_dump(),
        nights=nights,
        total_price=total_price
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/check-availability")
def check_availability(
    room_id: int,
    check_in: date,
    check_out: date,
    db: Session = Depends(get_db)
):
    conflict = db.query(Booking).filter(
        Booking.room_id == room_id,
        Booking.status != BookingStatus.cancelled,
        Booking.check_in < check_out,
        Booking.check_out > check_in
    ).first()
    return {"available": conflict is None}
