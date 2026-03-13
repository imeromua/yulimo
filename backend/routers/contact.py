"""Маршрут для форми зворотного зв'язку /api/contact."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.logging_config import error_logger
from database import get_db
from schemas.contact import ContactRequest
from services import smtp_email_service

router = APIRouter()
logger = logging.getLogger("yulimo.contact")

ADMIN_EMAIL = "info@yulimo.kyiv.ua"


@router.post("/contact")
async def send_contact_message(data: ContactRequest, db: Session = Depends(get_db)):
    """Приймає повідомлення з форми зворотного зв'язку та надсилає на пошту адміністрації."""
    subject = f"Нове повідомлення від {data.name}"
    body = (
        f"<p><strong>Ім'я:</strong> {data.name}</p>"
        f"<p><strong>Email:</strong> {data.email}</p>"
        f"<p><strong>Повідомлення:</strong></p>"
        f"<p>{data.message}</p>"
    )

    logger.info("Контактна форма: повідомлення від %s <%s>", data.name, data.email)

    try:
        await smtp_email_service.send_manual_email(
            recipient_email=ADMIN_EMAIL,
            subject=subject,
            body=body,
            db=db,
            recipient_name="Адміністрація Юлімо",
        )
    except Exception as exc:  # noqa: BLE001
        error_logger.error("Помилка надсилання контактного повідомлення: %s", exc)
        return {"success": False}

    return {"success": True}
