"""Сервіс бронювань: бізнес-логіка, перевірка перетину дат, транзакційна безпека."""

from datetime import date

from sqlalchemy import and_
from sqlalchemy.orm import Session

from core.logging_config import booking_logger
from models.booking import Booking, BookingStatus
from models.room import Room
from schemas.booking import BookingCreate


class BookingConflictError(Exception):
    pass


class RoomNotFoundError(Exception):
    pass


class InvalidDatesError(Exception):
    pass


def _check_conflict(
    db: Session,
    room_id: int,
    check_in: date,
    check_out: date,
    exclude_booking_id: int | None = None,
) -> bool:
    """Повертає True, якщо існує конфліктне бронювання (SELECT FOR UPDATE)."""
    q = (
        db.query(Booking)
        .filter(
            and_(
                Booking.room_id == room_id,
                Booking.status != BookingStatus.cancelled,
                Booking.check_in < check_out,
                Booking.check_out > check_in,
            )
        )
        .with_for_update()
    )
    if exclude_booking_id:
        q = q.filter(Booking.id != exclude_booking_id)
    return q.first() is not None


def create_booking(data: BookingCreate, db: Session) -> Booking:
    """Створює нове бронювання з захистом від перегонів (SELECT FOR UPDATE)."""
    room = db.query(Room).filter(Room.id == data.room_id, Room.is_active == True).first()
    if not room:
        raise RoomNotFoundError("Номер не знайдено або недоступний")

    # Транзакційна перевірка з блокуванням рядка
    with db.begin_nested():
        if _check_conflict(db, data.room_id, data.check_in, data.check_out):
            raise BookingConflictError("Номер зайнятий на обрані дати")

        nights = (data.check_out - data.check_in).days
        total_price = nights * room.price

        booking = Booking(
            **data.model_dump(),
            nights=nights,
            total_price=total_price,
        )
        db.add(booking)

    db.commit()
    db.refresh(booking)
    booking_logger.info(
        "Нове бронювання #%d: кімната %d, %s — %s",
        booking.id,
        data.room_id,
        data.check_in,
        data.check_out,
    )
    return booking


def check_availability(
    db: Session, room_id: int, check_in: date, check_out: date
) -> bool:
    """Перевіряє доступність кімнати на задані дати."""
    return not _check_conflict(db, room_id, check_in, check_out)


def get_all_bookings(db: Session) -> list[Booking]:
    """Повертає всі бронювання, відсортовані від найновішого."""
    return db.query(Booking).order_by(Booking.created_at.desc()).all()


def update_booking_status(
    booking_id: int, status: BookingStatus, db: Session
) -> Booking:
    """Оновлює статус бронювання."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise RoomNotFoundError("Бронювання не знайдено")
    booking.status = status
    db.commit()
    db.refresh(booking)
    booking_logger.info("Статус бронювання #%d змінено на %s", booking_id, status)
    return booking
