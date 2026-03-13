"""Обробник перегляду номерів."""

import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import room_nav_keyboard
from bot.states import RoomStates
from core.config import settings
from database import SessionLocal
from services import room_service

logger = logging.getLogger("yulimo.bot")

router = Router()

BASE_URL = "https://yulimo.kyiv.ua"


def _room_photo_url(room) -> str | None:
    """Повертає URL фото номера або None."""
    # Спочатку перевіряємо поле photo (рядок)
    photo = getattr(room, "photo", None)
    if photo:
        if photo.startswith("http"):
            return photo
        return f"{BASE_URL}/images/{photo.lstrip('/')}"

    # Якщо є поле photos (список)
    photos = getattr(room, "photos", None) or []
    if photos:
        p = photos[0]
        if p.startswith("http"):
            return p
        return f"{BASE_URL}/images/{p.lstrip('/')}"

    return None


def _room_card(room, index: int, total: int) -> str:
    amenities_list = getattr(room, "amenities", None) or []
    amenities_str = ""
    if amenities_list:
        items = "\n".join(f"• {a}" for a in amenities_list)
        amenities_str = f"\n\n✨ *Зручності:*\n{items}"

    return (
        f"🏠 *{room.name}* ({index + 1}/{total})\n\n"
        f"👥 До {room.capacity} гостей\n"
        f"💰 {room.price:.0f} грн/ніч\n\n"
        f"📝 {room.description or '—'}"
        f"{amenities_str}"
    )


async def _send_room_card(
    message: Message,
    rooms: list,
    index: int,
    state: FSMContext,
) -> None:
    room = rooms[index]
    await state.update_data(room_index=index)

    card_text = _room_card(room, index, len(rooms))
    keyboard = room_nav_keyboard(index, len(rooms), room.id)

    photo_url = _room_photo_url(room)
    if photo_url:
        try:
            await message.answer_photo(
                photo=photo_url,
                caption=card_text,
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
            return
        except Exception as exc:
            logger.warning("Не вдалося надіслати фото для номера %s: %s", room.id, exc)

    # Fallback: text only
    await message.answer(card_text, parse_mode="Markdown", reply_markup=keyboard)


async def show_rooms(message: Message, state: FSMContext) -> None:
    """Entry point for 🏠 Номери — called from start.py text handler."""
    await state.clear()
    db = SessionLocal()
    try:
        rooms = room_service.get_active_rooms(db)
    except Exception as exc:
        logger.error("Помилка отримання номерів: %s", exc)
        await message.answer("⚠️ Виникла помилка. Спробуйте ще раз.")
        return
    finally:
        db.close()

    if not rooms:
        await message.answer("😔 На жаль, наразі немає доступних номерів.")
        return

    await state.set_state(RoomStates.browsing)
    await state.update_data(room_ids=[r.id for r in rooms])
    await _send_room_card(message, rooms, 0, state)


@router.callback_query(lambda c: c.data == "menu:rooms")
async def cb_rooms(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    db = SessionLocal()
    try:
        rooms = room_service.get_active_rooms(db)
    except Exception as exc:
        logger.error("Помилка отримання номерів: %s", exc)
        await callback.message.answer("⚠️ Виникла помилка. Спробуйте ще раз.")
        await callback.answer()
        return
    finally:
        db.close()

    if not rooms:
        await callback.message.answer("😔 На жаль, наразі немає доступних номерів.")
        await callback.answer()
        return

    await state.set_state(RoomStates.browsing)
    await state.update_data(room_ids=[r.id for r in rooms])
    await callback.answer()
    await _send_room_card(callback.message, rooms, 0, state)


@router.callback_query(lambda c: c.data in ("room_nav:prev", "room_nav:next"))
async def cb_room_nav(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    room_ids: list[int] = data.get("room_ids", [])
    current_index: int = data.get("room_index", 0)

    if not room_ids:
        await callback.answer()
        return

    if callback.data == "room_nav:prev":
        new_index = max(0, current_index - 1)
    else:
        new_index = min(len(room_ids) - 1, current_index + 1)

    if new_index == current_index:
        await callback.answer()
        return

    db = SessionLocal()
    try:
        rooms = room_service.get_active_rooms(db)
    except Exception as exc:
        logger.error("Помилка отримання номерів: %s", exc)
        await callback.answer()
        return
    finally:
        db.close()

    if not rooms:
        await callback.answer()
        return

    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.answer()
    await _send_room_card(callback.message, rooms, new_index, state)


@router.callback_query(lambda c: c.data and c.data.startswith("room_nav:book:"))
async def cb_room_nav_book(callback: CallbackQuery, state: FSMContext) -> None:
    room_id = int(callback.data.split(":")[2])
    await state.update_data(room_id=room_id)
    from bot.keyboards import quick_date_keyboard
    from bot.states import BookingStates

    await state.set_state(BookingStates.enter_checkin)
    await callback.message.answer(
        "📅 Введіть дату заїзду (ДД.ММ.РРРР):",
        reply_markup=quick_date_keyboard(),
    )
    await callback.answer()
