"""Обробник FSM-бронювання номерів."""

import logging
from datetime import date, datetime

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import (
    back_to_menu_keyboard,
    cancel_keyboard,
    confirm_keyboard,
    rooms_list_keyboard,
)
from bot.states import BookingStates
from core.config import settings
from database import SessionLocal
from schemas.booking import BookingCreate
from services import booking_service, room_service
from services.booking_service import BookingConflictError
from services.email_service import _is_enabled, _send, _wrap_html

logger = logging.getLogger("yulimo.bot")

router = Router()

DATE_FORMAT = "%d.%m.%Y"


def _parse_date(text: str) -> date | None:
    try:
        return datetime.strptime(text.strip(), DATE_FORMAT).date()
    except ValueError:
        return None


@router.callback_query(lambda c: c.data == "menu:booking")
async def cb_start_booking(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    db = SessionLocal()
    try:
        rooms = room_service.get_active_rooms(db)
    except Exception as exc:
        logger.error("Помилка отримання номерів: %s", exc)
        rooms = []
    finally:
        db.close()

    if not rooms:
        await callback.message.edit_text(
            "😔 На жаль, наразі немає доступних номерів.",
            reply_markup=back_to_menu_keyboard(),
        )
        await callback.answer()
        return

    await state.set_state(BookingStates.select_room)
    await callback.message.edit_text(
        "🏠 Оберіть номер для бронювання:",
        reply_markup=rooms_list_keyboard(rooms),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("book_room:"))
async def cb_book_room(callback: CallbackQuery, state: FSMContext) -> None:
    room_id = int(callback.data.split(":")[1])
    await state.update_data(room_id=room_id)
    await state.set_state(BookingStates.enter_checkin)
    await callback.message.edit_text(
        "📅 Введіть дату заїзду (ДД.ММ.РРРР):",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(BookingStates.enter_checkin)
async def booking_checkin(message: Message, state: FSMContext) -> None:
    parsed = _parse_date(message.text or "")
    if parsed is None:
        await message.answer(
            "⚠️ Невірний формат дати. Введіть дату у форматі ДД.ММ.РРРР (наприклад: 25.06.2025):",
            reply_markup=cancel_keyboard(),
        )
        return
    if parsed < date.today():
        await message.answer(
            "⚠️ Дата заїзду не може бути в минулому. Введіть актуальну дату:",
            reply_markup=cancel_keyboard(),
        )
        return
    await state.update_data(check_in=parsed.isoformat())
    await state.set_state(BookingStates.enter_checkout)
    await message.answer(
        "📅 Введіть дату виїзду (ДД.ММ.РРРР):",
        reply_markup=cancel_keyboard(),
    )


@router.message(BookingStates.enter_checkout)
async def booking_checkout(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    check_in = date.fromisoformat(data["check_in"])
    parsed = _parse_date(message.text or "")
    if parsed is None:
        await message.answer(
            "⚠️ Невірний формат дати. Введіть дату у форматі ДД.ММ.РРРР:",
            reply_markup=cancel_keyboard(),
        )
        return
    if parsed <= check_in:
        await message.answer(
            "⚠️ Дата виїзду має бути пізніше дати заїзду. Введіть дату виїзду:",
            reply_markup=cancel_keyboard(),
        )
        return
    await state.update_data(check_out=parsed.isoformat())
    await state.set_state(BookingStates.enter_name)
    await message.answer(
        "👤 Ваше ім'я та прізвище:",
        reply_markup=cancel_keyboard(),
    )


@router.message(BookingStates.enter_name)
async def booking_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer(
            "⚠️ Ім'я занадто коротке. Введіть ім'я та прізвище:",
            reply_markup=cancel_keyboard(),
        )
        return
    await state.update_data(guest_name=name)
    await state.set_state(BookingStates.enter_phone)
    await message.answer(
        "📱 Номер телефону (напр. +380XXXXXXXXX):",
        reply_markup=cancel_keyboard(),
    )


@router.message(BookingStates.enter_phone)
async def booking_phone(message: Message, state: FSMContext) -> None:
    phone = (message.text or "").strip()
    if len(phone) < 7:
        await message.answer(
            "⚠️ Невірний номер телефону. Введіть номер у форматі +380XXXXXXXXX:",
            reply_markup=cancel_keyboard(),
        )
        return
    await state.update_data(guest_phone=phone)
    await state.set_state(BookingStates.enter_email)
    await message.answer(
        "📧 Email (необов'язково, натисніть /skip щоб пропустити):",
        reply_markup=cancel_keyboard(),
    )


@router.message(BookingStates.enter_email, Command("skip"))
async def booking_email_skip(message: Message, state: FSMContext) -> None:
    await state.update_data(guest_email=None)
    await state.set_state(BookingStates.enter_guests)
    await message.answer(
        "👥 Кількість гостей:",
        reply_markup=cancel_keyboard(),
    )


@router.message(BookingStates.enter_email)
async def booking_email(message: Message, state: FSMContext) -> None:
    email = (message.text or "").strip()
    await state.update_data(guest_email=email if email else None)
    await state.set_state(BookingStates.enter_guests)
    await message.answer(
        "👥 Кількість гостей:",
        reply_markup=cancel_keyboard(),
    )


@router.message(BookingStates.enter_guests)
async def booking_guests(message: Message, state: FSMContext) -> None:
    try:
        guests = int((message.text or "").strip())
        if guests < 1 or guests > 20:
            raise ValueError
    except ValueError:
        await message.answer(
            "⚠️ Введіть коректну кількість гостей (від 1 до 20):",
            reply_markup=cancel_keyboard(),
        )
        return

    data = await state.get_data()
    await state.update_data(guests_count=guests)

    db = SessionLocal()
    try:
        room = room_service.get_room_by_id(data["room_id"], db)
        room_name = room.name
        price_per_night = room.price
    except Exception:
        room_name = f"#{data['room_id']}"
        price_per_night = 0.0
    finally:
        db.close()

    check_in = date.fromisoformat(data["check_in"])
    check_out = date.fromisoformat(data["check_out"])
    nights = (check_out - check_in).days
    total = nights * price_per_night

    await state.update_data(room_name=room_name, price_per_night=price_per_night)
    await state.set_state(BookingStates.confirm)

    confirm_text = (
        "📋 <b>Підтвердження бронювання</b>\n\n"
        f"🏠 Номер: {room_name}\n"
        f"📅 Заїзд: {check_in.strftime(DATE_FORMAT)}\n"
        f"📅 Виїзд: {check_out.strftime(DATE_FORMAT)}\n"
        f"🌙 Ночей: {nights}\n"
        f"👥 Гостей: {guests}\n"
        f"💰 Сума: {total:.0f} грн\n"
        f"👤 Гість: {data['guest_name']}\n"
        f"📱 Телефон: {data['guest_phone']}"
    )
    await message.answer(
        confirm_text,
        parse_mode="HTML",
        reply_markup=confirm_keyboard("booking"),
    )


@router.callback_query(lambda c: c.data == "booking:cancel")
async def booking_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    from bot.handlers.start import WELCOME_TEXT
    from bot.keyboards import main_menu_keyboard

    await state.clear()
    await callback.message.edit_text(WELCOME_TEXT, reply_markup=main_menu_keyboard())
    await callback.answer("❌ Бронювання скасовано")


@router.callback_query(lambda c: c.data == "booking:confirm")
async def booking_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()

    db = SessionLocal()
    try:
        booking_data = BookingCreate(
            room_id=data["room_id"],
            guest_name=data["guest_name"],
            guest_phone=data["guest_phone"],
            guest_email=data.get("guest_email"),
            check_in=date.fromisoformat(data["check_in"]),
            check_out=date.fromisoformat(data["check_out"]),
            guests_count=data["guests_count"],
        )
        booking = booking_service.create_booking(booking_data, db)
        room_name = data.get("room_name", f"#{data['room_id']}")
    except BookingConflictError:
        await callback.message.edit_text(
            "😔 На жаль, цей номер вже зайнятий на обрані дати. Оберіть інший.",
            reply_markup=back_to_menu_keyboard(),
        )
        await callback.answer()
        return
    except Exception as exc:
        logger.error("Помилка створення бронювання: %s", exc)
        await callback.message.edit_text(
            "⚠️ Виникла помилка. Спробуйте ще раз або зверніться до адміністратора.",
            reply_markup=back_to_menu_keyboard(),
        )
        await callback.answer()
        return
    finally:
        db.close()

    # Email адміну
    if _is_enabled():
        check_in = date.fromisoformat(data["check_in"])
        check_out = date.fromisoformat(data["check_out"])
        nights = (check_out - check_in).days
        total = nights * data.get("price_per_night", 0)
        subject = f"🏠 Нове бронювання №{booking.id} від {booking.guest_name}"
        body = (
            '<h2 style="color:#2d5a27;margin-top:0;">Нове бронювання через бота</h2>'
            '<table style="width:100%;border-collapse:collapse;">'
            f'<tr><td style="padding:6px 0;color:#555;">Номер:</td><td><strong>{room_name}</strong></td></tr>'
            f'<tr><td style="padding:6px 0;color:#555;">Гість:</td><td>{booking.guest_name}</td></tr>'
            f'<tr><td style="padding:6px 0;color:#555;">Телефон:</td><td>{booking.guest_phone}</td></tr>'
            f'<tr><td style="padding:6px 0;color:#555;">Заїзд:</td><td>{check_in.strftime(DATE_FORMAT)}</td></tr>'
            f'<tr><td style="padding:6px 0;color:#555;">Виїзд:</td><td>{check_out.strftime(DATE_FORMAT)}</td></tr>'
            f'<tr><td style="padding:6px 0;color:#555;">Ночей:</td><td>{nights}</td></tr>'
            f'<tr><td style="padding:6px 0;color:#555;">Сума:</td><td><strong>{total:.0f} грн</strong></td></tr>'
            '</table>'
        )
        try:
            await _send(
                settings.NOTIFICATION_ADMIN_EMAIL,
                subject,
                _wrap_html(subject, body),
            )
        except Exception as exc:
            logger.error("Помилка email адміну: %s", exc)

    # Telegram сповіщення адміну
    if settings.TELEGRAM_ADMIN_CHAT_ID:
        from bot.main import bot as _bot
        if _bot is not None:
            try:
                check_in = date.fromisoformat(data["check_in"])
                check_out = date.fromisoformat(data["check_out"])
                admin_text = (
                    "🔔 <b>Нове бронювання через бота!</b>\n"
                    f"#{booking.id} {room_name}\n"
                    f"📅 {check_in.strftime(DATE_FORMAT)} — {check_out.strftime(DATE_FORMAT)}\n"
                    f"👤 {booking.guest_name} | 📱 {booking.guest_phone}"
                )
                await _bot.send_message(
                    settings.TELEGRAM_ADMIN_CHAT_ID,
                    admin_text,
                    parse_mode="HTML",
                )
            except Exception as exc:
                logger.error("Помилка Telegram сповіщення: %s", exc)

    await callback.message.edit_text(
        f"✅ <b>Бронювання №{booking.id} прийнято!</b>\n"
        "Статус: очікує підтвердження\n"
        "Адміністрація зв'яжеться з вами найближчим часом.",
        parse_mode="HTML",
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()
