"""Обробник FSM-резервації столика в ресторані."""

import logging
from datetime import date, datetime, time

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_to_menu_keyboard, cancel_keyboard, confirm_keyboard
from bot.states import TableStates
from core.config import settings
from database import SessionLocal
from schemas.restaurant import TableReservationCreate
from services import email_service, restaurant_service

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
    await callback.message.edit_text(
        "🍽️ <b>Резервація столика</b>\n\nВведіть дату (формат: ДД.ММ.РРРР):",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(TableStates.enter_date)
async def table_date(message: Message, state: FSMContext) -> None:
    parsed = _parse_date(message.text or "")
    if parsed is None:
        await message.answer(
            "⚠️ Невірний формат дати. Введіть дату у форматі ДД.ММ.РРРР (наприклад: 25.06.2025):",
            reply_markup=cancel_keyboard(),
        )
        return
    if parsed < date.today():
        await message.answer(
            "⚠️ Дата не може бути в минулому. Введіть актуальну дату:",
            reply_markup=cancel_keyboard(),
        )
        return
    await state.update_data(date=parsed.isoformat())
    await state.set_state(TableStates.enter_time)
    await message.answer(
        "🕐 Введіть час резервації (формат: ГГ:ХХ, наприклад 18:30):",
        reply_markup=cancel_keyboard(),
    )


@router.message(TableStates.enter_time)
async def table_time(message: Message, state: FSMContext) -> None:
    parsed = _parse_time(message.text or "")
    if parsed is None:
        await message.answer(
            "⚠️ Невірний формат часу. Введіть час у форматі ГГ:ХХ (наприклад: 18:30):",
            reply_markup=cancel_keyboard(),
        )
        return
    await state.update_data(time=parsed.strftime(TIME_FORMAT))
    await state.set_state(TableStates.enter_guests)
    await message.answer(
        "👥 Кількість гостей:",
        reply_markup=cancel_keyboard(),
    )


@router.message(TableStates.enter_guests)
async def table_guests(message: Message, state: FSMContext) -> None:
    try:
        guests = int((message.text or "").strip())
        if guests < 1 or guests > 50:
            raise ValueError
    except ValueError:
        await message.answer(
            "⚠️ Введіть коректну кількість гостей (від 1 до 50):",
            reply_markup=cancel_keyboard(),
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
    from bot.keyboards import main_menu_keyboard
    from bot.handlers.start import WELCOME_TEXT

    await state.clear()
    await callback.message.edit_text(WELCOME_TEXT, reply_markup=main_menu_keyboard())
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

    # Email notification to admin
    try:
        await email_service.send_table_reservation_notification_admin(reservation)
    except Exception as exc:
        logger.error("Помилка відправки email адміну: %s", exc)

    # Telegram notification to admin
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
                logger.error("Помилка відправки Telegram сповіщення адміну: %s", exc)

    await callback.message.edit_text(
        f"✅ <b>Резервацію №{reservation.id} прийнято!</b>\n"
        "Статус: очікує підтвердження\n"
        "Адміністрація зв'яжеться з вами найближчим часом.",
        parse_mode="HTML",
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()
