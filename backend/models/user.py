from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    email      = Column(String(100), unique=True, nullable=False)
    password   = Column(String(255), nullable=False)
    name       = Column(String(100))
    role       = Column(String(20), default="admin")  # admin | superadmin
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
