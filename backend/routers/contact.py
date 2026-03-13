"""Маршрут для форми зворотного зв'язку /api/contact."""

import logging

from fastapi import APIRouter

from core.config import settings
from core.logging_config import error_logger
from schemas.contact import ContactRequest
from services.email_service import _is_enabled, _send, _wrap_html

router = APIRouter()
logger = logging.getLogger("yulimo.contact")


@router.post("/contact")
async def send_contact_message(data: ContactRequest):
    """Приймає повідомлення з форми зворотного зв'язку та надсилає на пошту адміністрації."""
    logger.info("Контактна форма: повідомлення від %s <%s>", data.name, data.email)

    if _is_enabled():
        subject = f"📩 Нове звернення від {data.name}"
        body = (
            '<h2 style="color:#2d5a27;margin-top:0;">Нове звернення з сайту</h2>'
            '<table style="width:100%;border-collapse:collapse;">'
            f'<tr><td style="padding:8px 0;color:#555;">Ім\'я:</td>'
            f'<td style="padding:8px 0;"><strong>{data.name}</strong></td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Email:</td>'
            f'<td style="padding:8px 0;"><a href="mailto:{data.email}">{data.email}</a></td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;vertical-align:top;">Повідомлення:</td>'
            f'<td style="padding:8px 0;">{data.message}</td></tr>'
            '</table>'
        )
        try:
            await _send(
                settings.NOTIFICATION_ADMIN_EMAIL,
                subject,
                _wrap_html(subject, body),
            )
        except Exception as exc:  # noqa: BLE001
            error_logger.error("Помилка надсилання контактного повідомлення: %s", exc)
            return {"success": False}

    return {"success": True}
