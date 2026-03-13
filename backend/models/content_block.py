from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.sql import func

from database import Base


class ContentBlock(Base):
    __tablename__ = "content_blocks"

    key        = Column(String(100), primary_key=True)
    label      = Column(String(200), nullable=False)
    value      = Column(Text, nullable=False, default="")
    block_type = Column(String(20), default="text")  # text|html|number|boolean
    section    = Column(String(50), default="other")  # hero|about|rooms|restaurant|services|footer
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
