"""Клавіатури для Telegram-бота."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏠 Номери", callback_data="menu:rooms"),
        InlineKeyboardButton(text="📅 Перевірити дати", callback_data="menu:availability"),
    )
    builder.row(
        InlineKeyboardButton(text="📋 Забронювати", callback_data="menu:booking"),
        InlineKeyboardButton(text="🍽️ Ресторан", callback_data="menu:restaurant"),
    )
    builder.row(
        InlineKeyboardButton(text="📞 Контакти", callback_data="menu:contacts"),
        InlineKeyboardButton(text="❓ Правила", callback_data="menu:rules"),
    )
    return builder.as_markup()


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="← Назад", callback_data="menu:main"))
    return builder.as_markup()


def room_book_keyboard(room_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📋 Забронювати цей номер",
            callback_data=f"book_room:{room_id}",
        )
    )
    builder.row(InlineKeyboardButton(text="← Назад", callback_data="menu:main"))
    return builder.as_markup()


def rooms_list_keyboard(rooms: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for room in rooms:
        builder.row(
            InlineKeyboardButton(
                text=f"🏠 {room.name}",
                callback_data=f"book_room:{room.id}",
            )
        )
    builder.row(InlineKeyboardButton(text="← Назад", callback_data="menu:main"))
    return builder.as_markup()


def available_rooms_keyboard(rooms: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for room in rooms:
        builder.row(
            InlineKeyboardButton(
                text=f"📋 Забронювати — {room.name}",
                callback_data=f"book_room:{room.id}",
            )
        )
    builder.row(InlineKeyboardButton(text="← Назад", callback_data="menu:main"))
    return builder.as_markup()


def confirm_keyboard(prefix: str = "booking") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Підтвердити", callback_data=f"{prefix}:confirm"),
        InlineKeyboardButton(text="❌ Скасувати", callback_data=f"{prefix}:cancel"),
    )
    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel"))
    return builder.as_markup()
