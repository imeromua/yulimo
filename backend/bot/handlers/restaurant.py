"""Обробник FSM-резервації столика в ресторані."""

import logging
from datetime import date, datetime, time, timedelta

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import (
    back_to_menu_keyboard,
    cancel_keyboard,
    confirm_keyboard,
    quick_date_keyboard,
    quick_guests_keyboard,
    quick_time_keyboard,
)
from bot.states import TableStates
from core.config import settings
from database import SessionLocal
from schemas.restaurant import TableReservationCreate
from services import restaurant_service
from services.email_service import _is_enabled, _send, _wrap_html

logger = logging.getLogger("yulimo.bot")

router = Router()

DATE_FORMAT = "%d.%m.%Y"
TIME_FORMAT = "%H:%M"


def _parse_date(text: str) -> date | None:
    try:
        return datetime.strptime(text.strip(), DATE_FORMAT).date()
    except ValueError:
        return None


def _parse_time(text: str) -> time | None:
    try:
        return datetime.strptime(text.strip(), TIME_FORMAT).time()
    except ValueError:
        return None


@router.callback_query(lambda c: c.data == "menu:restaurant")
async def cb_restaurant(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(TableStates.enter_date)
    await callback.message.answer(
        "🍽️ <b>Резервація столика</b>\n\nВведіть дату (формат: ДД.ММ.РРРР):",
        parse_mode="HTML",
        reply_markup=quick_date_keyboard(),
    )
    await callback.answer()


# ── Quick-date callbacks for restaurant ───────────────────────────────────────

@router.callback_query(TableStates.enter_date, lambda c: c.data and c.data.startswith("quick_date:"))
async def restaurant_quick_date(callback: CallbackQuery, state: FSMContext) -> None:
    today = date.today()
    key = callback.data.split(":")[1]
    if key == "today":
        chosen = today
    elif key == "tomorrow":
        chosen = today + timedelta(days=1)
    else:
        chosen = today + timedelta(weeks=1)

    await state.update_data(date=chosen.isoformat())
    await state.set_state(TableStates.enter_time)
    await callback.message.answer(
        f"✅ Дата: {chosen.strftime(DATE_FORMAT)}\n\n🕐 Введіть час резервації (формат: ГГ:ХХ):",
        reply_markup=quick_time_keyboard(),
    )
    await callback.answer()


@router.message(TableStates.enter_date)
async def table_date(message: Message, state: FSMContext) -> None:
    parsed = _parse_date(message.text or "")
    if parsed is None:
        await message.answer(
            "⚠️ Невірний формат дати. Введіть дату у форматі ДД.ММ.РРРР (наприклад: 25.06.2025):",
            reply_markup=quick_date_keyboard(),
        )
        return
    if parsed < date.today():
        await message.answer(
            "⚠️ Дата не може бути в минулому. Введіть актуальну дату:",
            reply_markup=quick_date_keyboard(),
        )
        return
    await state.update_data(date=parsed.isoformat())
    await state.set_state(TableStates.enter_time)
    await message.answer(
        "🕐 Введіть час резервації (формат: ГГ:ХХ, наприклад 18:30):",
        reply_markup=quick_time_keyboard(),
    )


# ── Quick-time callbacks ───────────────────────────────────────────────────────

@router.callback_query(TableStates.enter_time, lambda c: c.data and c.data.startswith("quick_time:"))
async def restaurant_quick_time(callback: CallbackQuery, state: FSMContext) -> None:
    # callback_data is "quick_time:HH:MM" — rejoin after first colon
    time_str = callback.data[len("quick_time:"):]
    await state.update_data(time=time_str)
    await state.set_state(TableStates.enter_guests)
    await callback.message.answer(
        f"✅ Час: {time_str}\n\n👥 Кількість гостей:",
        reply_markup=quick_guests_keyboard(),
    )
    await callback.answer()


@router.message(TableStates.enter_time)
async def table_time(message: Message, state: FSMContext) -> None:
    parsed = _parse_time(message.text or "")
    if parsed is None:
        await message.answer(
            "⚠️ Невірний формат часу. Введіть час у форматі ГГ:ХХ (наприклад: 18:30):",
            reply_markup=quick_time_keyboard(),
        )
        return
    await state.update_data(time=parsed.strftime(TIME_FORMAT))
    await state.set_state(TableStates.enter_guests)
    await message.answer(
        "👥 Кількість гостей:",
        reply_markup=quick_guests_keyboard(),
    )


# ── Quick-guests callbacks ────────────────────────────────────────────────────

@router.callback_query(TableStates.enter_guests, lambda c: c.data and c.data.startswith("quick_guests:"))
async def restaurant_quick_guests(callback: CallbackQuery, state: FSMContext) -> None:
    guests = int(callback.data.split(":")[1])
    await state.update_data(guests_count=guests)
    await state.set_state(TableStates.enter_name)
    await callback.message.answer(
        f"✅ Гостей: {guests}\n\n👤 Ваше ім'я та прізвище:",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(TableStates.enter_guests)
async def table_guests(message: Message, state: FSMContext) -> None:
    try:
        guests = int((message.text or "").strip())
        if guests < 1 or guests > 50:
            raise ValueError
    except ValueError:
        await message.answer(
            "⚠️ Введіть коректну кількість гостей (від 1 до 50):",
            reply_markup=quick_guests_keyboard(),
        )
        return
    await state.update_data(guests_count=guests)
    await state.set_state(TableStates.enter_name)
    await message.answer(
        "👤 Ваше ім'я та прізвище:",
        reply_markup=cancel_keyboard(),
    )


@router.message(TableStates.enter_name)
async def table_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer(
            "⚠️ Ім'я занадто коротке. Введіть ім'я та прізвище:",
            reply_markup=cancel_keyboard(),
        )
        return
    await state.update_data(guest_name=name)
    await state.set_state(TableStates.enter_phone)
    await message.answer(
        "📱 Номер телефону (напр. +380XXXXXXXXX):",
        reply_markup=cancel_keyboard(),
    )


@router.message(TableStates.enter_phone)
async def table_phone(message: Message, state: FSMContext) -> None:
    phone = (message.text or "").strip()
    if len(phone) < 7:
        await message.answer(
            "⚠️ Невірний номер телефону. Введіть номер у форматі +380XXXXXXXXX:",
            reply_markup=cancel_keyboard(),
        )
        return
    await state.update_data(guest_phone=phone)
    data = await state.get_data()
    await state.set_state(TableStates.confirm)

    rsv_date = date.fromisoformat(data["date"])
    confirm_text = (
        "🍽️ <b>Підтвердження резервації столика</b>\n\n"
        f"📅 Дата: {rsv_date.strftime(DATE_FORMAT)}\n"
        f"🕐 Час: {data['time']}\n"
        f"👥 Гостей: {data['guests_count']}\n"
        f"👤 Ім'я: {data['guest_name']}\n"
        f"📱 Телефон: {phone}"
    )
    await message.answer(
        confirm_text,
        parse_mode="HTML",
        reply_markup=confirm_keyboard("table"),
    )


@router.callback_query(lambda c: c.data == "table:cancel")
async def table_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    from bot.handlers.start import WELCOME_TEXT
    from bot.keyboards import main_menu_keyboard

    await state.clear()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        "❌ Резервацію скасовано.\n\n" + WELCOME_TEXT,
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer("❌ Резервацію скасовано")


@router.callback_query(lambda c: c.data == "table:confirm")
async def table_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()

    db = SessionLocal()
    try:
        rsv_date = date.fromisoformat(data["date"])
        rsv_time = datetime.strptime(data["time"], TIME_FORMAT).time()
        rsv_data = TableReservationCreate(
            guest_name=data["guest_name"],
            guest_phone=data["guest_phone"],
            date=rsv_date,
            time=rsv_time,
            guests_count=data["guests_count"],
        )
        reservation = restaurant_service.create_table_reservation(rsv_data, db)
    except Exception as exc:
        logger.error("Помилка створення резервації: %s", exc)
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
        subject = f"🍽️ Нова резервація столика від {reservation.guest_name}"
        body = (
            '<h2 style="color:#2d5a27;margin-top:0;">Нова резервація через бота</h2>'
            '<table style="width:100%;border-collapse:collapse;">'
            f'<tr><td style="padding:6px 0;color:#555;">Ім\'я:</td><td><strong>{reservation.guest_name}</strong></td></tr>'
            f'<tr><td style="padding:6px 0;color:#555;">Телефон:</td><td>{reservation.guest_phone}</td></tr>'
            f'<tr><td style="padding:6px 0;color:#555;">Дата:</td><td>{reservation.date.strftime(DATE_FORMAT)}</td></tr>'
            f'<tr><td style="padding:6px 0;color:#555;">Час:</td><td>{reservation.time.strftime(TIME_FORMAT)}</td></tr>'
            f'<tr><td style="padding:6px 0;color:#555;">Гостей:</td><td>{reservation.guests_count}</td></tr>'
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
                admin_text = (
                    "🔔 <b>Нова резервація столика через бота!</b>\n"
                    f"#{reservation.id}\n"
                    f"📅 {reservation.date.strftime(DATE_FORMAT)} о {reservation.time.strftime(TIME_FORMAT)}\n"
                    f"👥 {reservation.guests_count} гостей\n"
                    f"👤 {reservation.guest_name} | 📱 {reservation.guest_phone}"
                )
                await _bot.send_message(
                    settings.TELEGRAM_ADMIN_CHAT_ID,
                    admin_text,
                    parse_mode="HTML",
                )
            except Exception as exc:
                logger.error("Помилка Telegram сповіщення: %s", exc)

    await callback.message.edit_text(
        f"✅ <b>Резервацію №{reservation.id} прийнято!</b>\n"
        "Статус: очікує підтвердження\n"
        "Адміністрація зв'яжеться з вами найближчим часом.",
        parse_mode="HTML",
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()
