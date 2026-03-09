from sqlalchemy import Column, Integer, String, Float, Boolean, Text, Time, Date, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from database import Base
import enum


class MenuCategory(str, enum.Enum):
    starters  = "starters"   # Закуски
    soups     = "soups"      # Супи
    mains     = "mains"      # Основні страви
    grill     = "grill"      # Гриль
    desserts  = "desserts"   # Десерти
    drinks    = "drinks"     # Напої


class MenuItem(Base):
    __tablename__ = "menu_items"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    description = Column(Text)
    category    = Column(Enum(MenuCategory), nullable=False)
    price       = Column(Float, nullable=False)
    weight      = Column(String(20))   # "250 г"
    photo       = Column(String(255))
    is_active   = Column(Boolean, default=True)


class TableReservation(Base):
    __tablename__ = "table_reservations"

    id           = Column(Integer, primary_key=True, index=True)
    guest_name   = Column(String(100), nullable=False)
    guest_phone  = Column(String(20), nullable=False)
    date         = Column(Date, nullable=False)
    time         = Column(Time, nullable=False)
    guests_count = Column(Integer, nullable=False)
    comment      = Column(String(500))
    status       = Column(String(20), default="pending")
    created_at   = Column(DateTime, server_default=func.now())
