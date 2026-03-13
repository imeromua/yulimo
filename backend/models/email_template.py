from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from database import Base


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), unique=True, nullable=False)
    subject       = Column(String(255), nullable=False)
    body_html     = Column(Text, nullable=False)
    template_type = Column(String(50), unique=True, nullable=False)
    is_active     = Column(Boolean, default=True)
    updated_at    = Column(DateTime, server_default=func.now(), onupdate=func.now())
