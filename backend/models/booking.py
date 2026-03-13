from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class BookingStatus(str, enum.Enum):
    pending   = "pending"    # Очікує підтвердження
    confirmed = "confirmed"  # Підтверджено
    cancelled = "cancelled"  # Скасовано
    completed = "completed"  # Завершено


class Booking(Base):
    __tablename__ = "bookings"

    id           = Column(Integer, primary_key=True, index=True)
    room_id      = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    client_id    = Column(Integer, ForeignKey("clients.id"), nullable=True)
    # Дані гостя
    guest_name   = Column(String(100), nullable=False)
    guest_phone  = Column(String(20), nullable=False)
    guest_email  = Column(String(100))
    # Дати
    check_in     = Column(Date, nullable=False)
    check_out    = Column(Date, nullable=False)
    nights       = Column(Integer, nullable=False)
    guests_count = Column(Integer, default=1)
    # Фінанси
    total_price  = Column(Float, nullable=False)
    # Статус
    status       = Column(Enum(BookingStatus), default=BookingStatus.pending)
    comment      = Column(String(500))
    created_at   = Column(DateTime, server_default=func.now())

    client = relationship("Client", back_populates="bookings")
