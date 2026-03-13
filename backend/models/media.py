from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from database import Base


class Media(Base):
    __tablename__ = "media"

    id            = Column(Integer, primary_key=True, index=True)
    filename      = Column(String(255), unique=True, nullable=False)
    original_name = Column(String(255), nullable=False)
    section       = Column(String(50), nullable=False, default="other")  # gallery|rooms|restaurant|hero|other
    title_uk      = Column(String(255), nullable=True)
    sort_order    = Column(Integer, default=0)
    is_active     = Column(Boolean, default=True)
    uploaded_at   = Column(DateTime, server_default=func.now())
