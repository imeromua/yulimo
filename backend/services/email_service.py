"""Email-сервіс для відправки сповіщень через Resend."""

import asyncio
from typing import Any

from core.config import settings
from core.logging_config import error_logger

try:
    import resend as _resend_module

    _resend_available = True
except ImportError:  # pragma: no cover
    _resend_available = False


# --------------------------------------------------------------------------- #
# Внутрішні допоміжні функції                                                 #
# --------------------------------------------------------------------------- #

def _is_enabled() -> bool:
    """Перевіряє, чи налаштовано відправку email."""
    return bool(settings.RESEND_API_KEY) and _resend_available


def _footer_html() -> str:
    return (
        '<div style="margin-top:32px;padding-top:16px;border-top:1px solid #e0d8c0;'
        'font-size:12px;color:#888;text-align:center;">'
        "<p>База відпочинку <strong>Юлімо</strong> · Пуща-Водиця, Київ</p>"
        '<p>📞 +38 (073) 537-60-37 &nbsp;·&nbsp; '
        '<a href="https://yulimo.kyiv.ua" style="color:#2d5a27;">yulimo.kyiv.ua</a></p>'
        "</div>"
    )


def _wrap_html(title: str, body: str) -> str:
    return (
        '<!DOCTYPE html><html lang="uk"><head><meta charset="UTF-8">'
        f"<title>{title}</title></head>"
        '<body style="font-family:Arial,sans-serif;background:#f5f0e8;margin:0;padding:0;">'
        '<div style="max-width:600px;margin:0 auto;padding:24px;">'
        '<div style="background:#2d5a27;color:#fff;padding:20px 24px;'
        'border-radius:8px 8px 0 0;text-align:center;">'
        '<h1 style="margin:0;font-size:24px;letter-spacing:1px;">🌿 Юлімо</h1>'
        '<p style="margin:4px 0 0;font-size:13px;opacity:.85;">'
        "База відпочинку · Пуща-Водиця, Київ</p>"
        "</div>"
        '<div style="background:#fff;padding:24px;border-radius:0 0 8px 8px;">'
        f"{body}{_footer_html()}"
        "</div></div></body></html>"
    )


def _booking_details_html(booking: Any, room_name: str) -> str:
    display_name = room_name if room_name else f"#{booking.room_id}"
    comment_row = (
        f'<tr><td style="padding:8px 0;color:#555;vertical-align:top;">'
        f"Коментар:</td>"
        f'<td style="padding:8px 0;">{booking.comment}</td></tr>'
        if booking.comment
        else ""
    )
    return (
        '<table style="width:100%;border-collapse:collapse;">'
        f'<tr><td style="padding:8px 0;color:#555;">Номер бронювання:</td>'
        f'<td style="padding:8px 0;"><strong>№{booking.id}</strong></td></tr>'
        f'<tr><td style="padding:8px 0;color:#555;">Номер / котедж:</td>'
        f'<td style="padding:8px 0;"><strong>{display_name}</strong></td></tr>'
        f'<tr><td style="padding:8px 0;color:#555;">Дата заїзду:</td>'
        f'<td style="padding:8px 0;">{booking.check_in.strftime("%d.%m.%Y")}</td></tr>'
        f'<tr><td style="padding:8px 0;color:#555;">Дата виїзду:</td>'
        f'<td style="padding:8px 0;">{booking.check_out.strftime("%d.%m.%Y")}</td></tr>'
        f'<tr><td style="padding:8px 0;color:#555;">Кількість ночей:</td>'
        f'<td style="padding:8px 0;">{booking.nights}</td></tr>'
        f'<tr><td style="padding:8px 0;color:#555;">Кількість гостей:</td>'
        f'<td style="padding:8px 0;">{booking.guests_count}</td></tr>'
        f'<tr><td style="padding:8px 0;color:#555;">Сума до оплати:</td>'
        f'<td style="padding:8px 0;"><strong>{booking.total_price:.0f} грн</strong></td></tr>'
        f"{comment_row}"
        "</table>"
    )


def _send_sync(to: str, subject: str, html: str) -> None:
    """Синхронна відправка через Resend SDK."""
    _resend_module.api_key = settings.RESEND_API_KEY
    _resend_module.Emails.send(
        {
            "from": settings.FROM_EMAIL,
            "to": [to],
            "subject": subject,
            "html": html,
        }
    )


async def _send(to: str, subject: str, html: str) -> None:
    """Асинхронна обгортка навколо синхронного Resend SDK."""
    await asyncio.to_thread(_send_sync, to, subject, html)


# --------------------------------------------------------------------------- #
# Публічні функції                                                             #
# --------------------------------------------------------------------------- #

async def send_booking_confirmation(booking: Any, room_name: str = "") -> None:
    """Відправляє підтвердження бронювання клієнту."""
    if not _is_enabled():
        return
    if not booking.guest_email:
        return
    try:
        subject = f"Бронювання №{booking.id} підтверджено — Юлімо"
        body = (
            '<h2 style="color:#2d5a27;margin-top:0;">Ваше бронювання підтверджено! 🎉</h2>'
            '<p style="color:#555;">Дякуємо за вибір бази відпочинку Юлімо. '
            "Нижче наведено деталі вашого бронювання:</p>"
            f"{_booking_details_html(booking, room_name)}"
            '<p style="margin-top:20px;color:#555;">'
            "З питань та уточнень звертайтеся: "
            '<strong style="color:#2d5a27;">+38 (073) 537-60-37</strong></p>'
            '<p style="color:#888;font-size:13px;">Чекаємо вас!</p>'
        )
        await _send(booking.guest_email, subject, _wrap_html(subject, body))
    except Exception as exc:
        error_logger.error(
            "Помилка відправки підтвердження бронювання #%s клієнту: %s",
            getattr(booking, "id", "?"),
            exc,
        )


async def send_booking_status_update(booking: Any, new_status: str, room_name: str = "") -> None:
    """Відправляє клієнту сповіщення про зміну статусу бронювання."""
    if not _is_enabled():
        return
    if not booking.guest_email:
        return
    try:
        status_labels = {
            "confirmed": "✅ Підтверджено",
            "cancelled": "❌ Скасовано",
            "pending": "⏳ Очікує підтвердження",
            "completed": "🏁 Завершено",
        }
        status_str = str(new_status.value if hasattr(new_status, "value") else new_status)
        status_label = status_labels.get(status_str, status_str)

        subject = f"Статус бронювання №{booking.id} змінено — Юлімо"
        body = (
            '<h2 style="color:#2d5a27;margin-top:0;">Зміна статусу бронювання</h2>'
            f'<p style="font-size:16px;">Новий статус: <strong>{status_label}</strong></p>'
            f"{_booking_details_html(booking, room_name)}"
            '<p style="margin-top:20px;color:#555;">'
            "З питань звертайтеся: "
            '<strong style="color:#2d5a27;">+38 (073) 537-60-37</strong></p>'
        )
        await _send(booking.guest_email, subject, _wrap_html(subject, body))
    except Exception as exc:
        error_logger.error(
            "Помилка відправки зміни статусу бронювання #%s клієнту: %s",
            getattr(booking, "id", "?"),
            exc,
        )


async def send_booking_notification_admin(booking: Any, room_name: str = "") -> None:
    """Відправляє адміну сповіщення про нове бронювання."""
    if not _is_enabled():
        return
    try:
        subject = f"🔔 Нове бронювання №{booking.id} — {booking.guest_name}"
        comment_row = (
            f'<tr><td style="padding:8px 0;color:#555;vertical-align:top;">Коментар:</td>'
            f'<td style="padding:8px 0;">{booking.comment}</td></tr>'
            if booking.comment
            else ""
        )
        display_name = room_name if room_name else f"#{booking.room_id}"
        body = (
            '<h2 style="color:#2d5a27;margin-top:0;">Нове бронювання</h2>'
            '<table style="width:100%;border-collapse:collapse;">'
            f'<tr><td style="padding:8px 0;color:#555;">Номер бронювання:</td>'
            f'<td style="padding:8px 0;"><strong>№{booking.id}</strong></td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Гість:</td>'
            f'<td style="padding:8px 0;"><strong>{booking.guest_name}</strong></td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Телефон:</td>'
            f'<td style="padding:8px 0;">{booking.guest_phone}</td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Email:</td>'
            f'<td style="padding:8px 0;">{booking.guest_email or "—"}</td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Номер / котедж:</td>'
            f'<td style="padding:8px 0;"><strong>{display_name}</strong></td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Заїзд:</td>'
            f'<td style="padding:8px 0;">{booking.check_in.strftime("%d.%m.%Y")}</td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Виїзд:</td>'
            f'<td style="padding:8px 0;">{booking.check_out.strftime("%d.%m.%Y")}</td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Ночей:</td>'
            f'<td style="padding:8px 0;">{booking.nights}</td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Гостей:</td>'
            f'<td style="padding:8px 0;">{booking.guests_count}</td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Сума:</td>'
            f'<td style="padding:8px 0;"><strong>{booking.total_price:.0f} грн</strong></td></tr>'
            f"{comment_row}"
            "</table>"
        )
        await _send(
            settings.NOTIFICATION_ADMIN_EMAIL,
            subject,
            _wrap_html(subject, body),
        )
    except Exception as exc:
        error_logger.error(
            "Помилка відправки сповіщення адміну про бронювання #%s: %s",
            getattr(booking, "id", "?"),
            exc,
        )


async def send_table_reservation_confirmation(reservation: Any) -> None:
    """Відправляє підтвердження резервації столика клієнту."""
    if not _is_enabled():
        return
    if not getattr(reservation, "guest_email", None):
        return
    try:
        subject = "Резервація столика підтверджена — Юлімо"
        comment_row = (
            f'<tr><td style="padding:8px 0;color:#555;vertical-align:top;">Коментар:</td>'
            f'<td style="padding:8px 0;">{reservation.comment}</td></tr>'
            if getattr(reservation, "comment", None)
            else ""
        )
        body = (
            '<h2 style="color:#2d5a27;margin-top:0;">Вашу резервацію підтверджено! 🍽️</h2>'
            '<p style="color:#555;">Деталі вашої резервації столика в ресторані Юлімо:</p>'
            '<table style="width:100%;border-collapse:collapse;">'
            f'<tr><td style="padding:8px 0;color:#555;">Дата:</td>'
            f'<td style="padding:8px 0;">{reservation.date.strftime("%d.%m.%Y")}</td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Час:</td>'
            f'<td style="padding:8px 0;">{reservation.time.strftime("%H:%M")}</td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Кількість гостей:</td>'
            f'<td style="padding:8px 0;">{reservation.guests_count}</td></tr>'
            f"{comment_row}"
            "</table>"
            '<p style="margin-top:20px;color:#555;">'
            "З питань звертайтеся: "
            '<strong style="color:#2d5a27;">+38 (073) 537-60-37</strong></p>'
            '<p style="color:#888;font-size:13px;">Чекаємо вас!</p>'
        )
        await _send(reservation.guest_email, subject, _wrap_html(subject, body))
    except Exception as exc:
        error_logger.error(
            "Помилка відправки підтвердження резервації #%s клієнту: %s",
            getattr(reservation, "id", "?"),
            exc,
        )


async def send_table_reservation_notification_admin(reservation: Any) -> None:
    """Відправляє адміну сповіщення про нову резервацію столика."""
    if not _is_enabled():
        return
    try:
        subject = f"🔔 Нова резервація столика — {reservation.guest_name}"
        comment_row = (
            f'<tr><td style="padding:8px 0;color:#555;vertical-align:top;">Коментар:</td>'
            f'<td style="padding:8px 0;">{reservation.comment}</td></tr>'
            if getattr(reservation, "comment", None)
            else ""
        )
        body = (
            '<h2 style="color:#2d5a27;margin-top:0;">Нова резервація столика</h2>'
            '<table style="width:100%;border-collapse:collapse;">'
            f'<tr><td style="padding:8px 0;color:#555;">Гість:</td>'
            f'<td style="padding:8px 0;"><strong>{reservation.guest_name}</strong></td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Телефон:</td>'
            f'<td style="padding:8px 0;">{reservation.guest_phone}</td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Email:</td>'
            f'<td style="padding:8px 0;">{getattr(reservation, "guest_email", None) or "—"}</td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Дата:</td>'
            f'<td style="padding:8px 0;">{reservation.date.strftime("%d.%m.%Y")}</td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Час:</td>'
            f'<td style="padding:8px 0;">{reservation.time.strftime("%H:%M")}</td></tr>'
            f'<tr><td style="padding:8px 0;color:#555;">Кількість гостей:</td>'
            f'<td style="padding:8px 0;">{reservation.guests_count}</td></tr>'
            f"{comment_row}"
            "</table>"
        )
        await _send(
            settings.NOTIFICATION_ADMIN_EMAIL,
            subject,
            _wrap_html(subject, body),
        )
    except Exception as exc:
        error_logger.error(
            "Помилка відправки сповіщення адміну про резервацію #%s: %s",
            getattr(reservation, "id", "?"),
            exc,
        )
