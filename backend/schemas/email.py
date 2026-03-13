from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EmailLogRead(BaseModel):
    id: int
    recipient_email: str
    recipient_name: Optional[str] = None
    subject: str
    body: str
    template_type: Optional[str] = None
    status: str
    booking_id: Optional[int] = None
    sent_at: datetime
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


class EmailTemplateRead(BaseModel):
    id: int
    name: str
    subject: str
    body_html: str
    template_type: str
    is_active: bool
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmailTemplateUpdate(BaseModel):
    subject: Optional[str] = None
    body_html: Optional[str] = None
    is_active: Optional[bool] = None


class EmailSendManual(BaseModel):
    recipient_email: str
    recipient_name: Optional[str] = None
    subject: str
    body: str


class EmailStats(BaseModel):
    total: int
    sent: int
    failed: int
    pending: int
    by_type: dict
