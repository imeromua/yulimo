from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON
from database import Base


class Room(Base):
    __tablename__ = "rooms"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)        # Назва номеру
    type        = Column(String(50), nullable=False)         # standard | cottage | suite
    description = Column(Text)
    capacity    = Column(Integer, default=2)                 # Кількість гостей
    area        = Column(Float)                              # Площа м²
    price       = Column(Float, nullable=False)              # Ціна за ніч
    amenities   = Column(JSON, default=list)                 # ["wifi", "tv", "sauna"]
    photos      = Column(JSON, default=list)                 # ["url1", "url2"]
    is_active   = Column(Boolean, default=True)
