"""Email-сервіс через smtplib з логуванням до EmailLog."""

import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Optional

from sqlalchemy.orm import Session

from core.config import settings
from core.logging_config import error_logger
from models.email_log import EmailLog
from models.email_template import EmailTemplate


def _is_smtp_enabled() -> bool:
    return bool(getattr(settings, "SMTP_HOST", "") and getattr(settings, "SMTP_USER", ""))


def _log_email(
    db: Session,
    recipient_email: str,
    subject: str,
    body: str,
    status: str,
    recipient_name: Optional[str] = None,
    template_type: Optional[str] = None,
    booking_id: Optional[int] = None,
    error_message: Optional[str] = None,
) -> EmailLog:
    log = EmailLog(
        recipient_email=recipient_email,
        recipient_name=recipient_name,
        subject=subject,
        body=body,
        template_type=template_type,
        status=status,
        booking_id=booking_id,
        error_message=error_message,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def _send_smtp_sync(to: str, subject: str, html: str) -> None:
    smtp_host = getattr(settings, "SMTP_HOST", "")
    smtp_port = int(getattr(settings, "SMTP_PORT", 587))
    smtp_user = getattr(settings, "SMTP_USER", "")
    smtp_pass = getattr(settings, "SMTP_PASS", "")
    smtp_from = getattr(settings, "SMTP_FROM", smtp_user)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_from
    msg["To"] = to
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        if smtp_port != 25:
            server.starttls()
        if smtp_user:
            server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_from, [to], msg.as_string())


async def _send_smtp(to: str, subject: str, html: str) -> None:
    await asyncio.to_thread(_send_smtp_sync, to, subject, html)


def _render_template(body_html: str, context: dict) -> str:
    for key, value in context.items():
        body_html = body_html.replace("{{" + key + "}}", str(value) if value is not None else "")
    return body_html


async def send_manual_email(
    recipient_email: str,
    subject: str,
    body: str,
    db: Session,
    recipient_name: Optional[str] = None,
) -> EmailLog:
    """Надсилає довільний лист і логує результат."""
    error_msg = None
    result_status = "sent"
    try:
        if _is_smtp_enabled():
            await _send_smtp(recipient_email, subject, body)
    except Exception as exc:
        error_logger.error("Помилка відправки email до %s: %s", recipient_email, exc)
        error_msg = str(exc)
        result_status = "failed"

    return _log_email(
        db=db,
        recipient_email=recipient_email,
        recipient_name=recipient_name,
        subject=subject,
        body=body,
        status=result_status,
        template_type="manual",
        error_message=error_msg,
    )


async def send_template_for_booking(
    booking: Any,
    template_type: str,
    db: Session,
) -> EmailLog:
    """Надсилає шаблонний лист для бронювання."""
    template = db.query(EmailTemplate).filter(
        EmailTemplate.template_type == template_type,
        EmailTemplate.is_active == True,
    ).first()

    recipient_email = booking.guest_email or ""
    if not recipient_email:
        return _log_email(
            db=db,
            recipient_email="",
            recipient_name=booking.guest_name,
            subject="(no email)",
            body="",
            status="failed",
            template_type=template_type,
            booking_id=booking.id,
            error_message="Немає email адреси гостя",
        )

    if not template:
        return _log_email(
            db=db,
            recipient_email=recipient_email,
            recipient_name=booking.guest_name,
            subject="(no template)",
            body="",
            status="failed",
            template_type=template_type,
            booking_id=booking.id,
            error_message=f"Шаблон '{template_type}' не знайдено або неактивний",
        )

    context = {
        "guest_name": booking.guest_name,
        "check_in": booking.check_in.strftime("%d.%m.%Y") if booking.check_in else "",
        "check_out": booking.check_out.strftime("%d.%m.%Y") if booking.check_out else "",
        "nights": booking.nights,
        "total_price": f"{booking.total_price:.0f}",
        "room_name": f"#{booking.room_id}",
        "booking_id": booking.id,
    }
    rendered_body = _render_template(template.body_html, context)
    rendered_subject = _render_template(template.subject, context)

    error_msg = None
    result_status = "sent"
    try:
        if _is_smtp_enabled():
            await _send_smtp(recipient_email, rendered_subject, rendered_body)
    except Exception as exc:
        error_logger.error("Помилка відправки шаблону '%s' для бронювання #%s: %s", template_type, booking.id, exc)
        error_msg = str(exc)
        result_status = "failed"

    return _log_email(
        db=db,
        recipient_email=recipient_email,
        recipient_name=booking.guest_name,
        subject=rendered_subject,
        body=rendered_body,
        status=result_status,
        template_type=template_type,
        booking_id=booking.id,
        error_message=error_msg,
    )
