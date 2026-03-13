"""Обробник перевірки доступності номерів."""

import logging
from datetime import date, datetime

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_to_menu_keyboard, book_room_keyboard, cancel_keyboard
from bot.states import AvailabilityStates
from database import SessionLocal
from services import booking_service, room_service

logger = logging.getLogger("yulimo.bot")

router = Router()

DATE_FORMAT = "%d.%m.%Y"


def _parse_date(text: str) -> date | None:
    try:
        return datetime.strptime(text.strip(), DATE_FORMAT).date()
    except ValueError:
        return None


@router.callback_query(lambda c: c.data == "menu:availability")
async def cb_availability(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AvailabilityStates.enter_checkin)
    await callback.message.answer(
        "📅 Введіть дату заїзду (формат: ДД.ММ.РРРР):",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(AvailabilityStates.enter_checkin)
async def avail_checkin(message: Message, state: FSMContext) -> None:
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
    await state.set_state(AvailabilityStates.enter_checkout)
    await message.answer(
        "📅 Введіть дату виїзду (формат: ДД.ММ.РРРР):",
        reply_markup=cancel_keyboard(),
    )


@router.message(AvailabilityStates.enter_checkout)
async def avail_checkout(message: Message, state: FSMContext) -> None:
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

    await state.clear()

    db = SessionLocal()
    try:
        rooms = room_service.get_active_rooms(db)
        available = [
            r for r in rooms
            if booking_service.check_availability(db, r.id, check_in, parsed)
        ]
    except Exception as exc:
        logger.error("Помилка перевірки доступності: %s", exc)
        await message.answer(
            "⚠️ Виникла помилка. Спробуйте ще раз або зверніться до адміністратора.",
            reply_markup=back_to_menu_keyboard(),
        )
        return
    finally:
        db.close()

    if not available:
        await message.answer(
            "😔 На жаль, на обрані дати всі номери зайняті.",
            reply_markup=back_to_menu_keyboard(),
        )
        return

    await message.answer(
        f"✅ Доступні номери на {check_in.strftime(DATE_FORMAT)} — {parsed.strftime(DATE_FORMAT)}:"
    )
    for room in available:
        await message.answer(
            f"🏠 {room.name} — {room.price:.0f} грн/ніч (до {room.capacity} гостей)",
            reply_markup=book_room_keyboard(room.id),
        )
