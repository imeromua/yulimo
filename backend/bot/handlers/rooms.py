"""Обробник перегляду номерів."""

import logging

from aiogram import Router
from aiogram.types import CallbackQuery

from bot.keyboards import back_to_menu_keyboard, room_book_keyboard
from database import SessionLocal
from services import room_service

logger = logging.getLogger("yulimo.bot")

router = Router()


def _room_card(room) -> str:
    return (
        f"🏠 <b>{room.name}</b>\n"
        f"👥 До {room.capacity} гостей\n"
        f"💰 {room.price:.0f} грн/ніч\n"
        f"📝 {room.description or '—'}"
    )


@router.callback_query(lambda c: c.data == "menu:rooms")
async def cb_rooms(callback: CallbackQuery) -> None:
    db = SessionLocal()
    try:
        rooms = room_service.get_active_rooms(db)
    except Exception as exc:
        logger.error("Помилка отримання номерів: %s", exc)
        await callback.message.edit_text(
            "⚠️ Виникла помилка. Спробуйте ще раз або зверніться до адміністратора.",
            reply_markup=back_to_menu_keyboard(),
        )
        await callback.answer()
        return
    finally:
        db.close()

    if not rooms:
        await callback.message.edit_text(
            "😔 На жаль, наразі немає доступних номерів.",
            reply_markup=back_to_menu_keyboard(),
        )
        await callback.answer()
        return

    await callback.answer()
    await callback.message.delete()

    for room in rooms:
        await callback.message.answer(
            _room_card(room),
            parse_mode="HTML",
            reply_markup=room_book_keyboard(room.id),
        )
