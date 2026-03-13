from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from database import Base


class EmailLog(Base):
    __tablename__ = "email_logs"

    id               = Column(Integer, primary_key=True, index=True)
    recipient_email  = Column(String(100), nullable=False)
    recipient_name   = Column(String(100), nullable=True)
    subject          = Column(String(255), nullable=False)
    body             = Column(Text, nullable=False)
    template_type    = Column(String(50), nullable=True)  # booking_confirm|booking_reminder|birthday|manual|booking_cancelled
    status           = Column(String(20), default="pending")  # sent|failed|pending
    booking_id       = Column(Integer, nullable=True)
    sent_at          = Column(DateTime, server_default=func.now())
    error_message    = Column(Text, nullable=True)
