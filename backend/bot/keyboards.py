"""Клавіатури для Telegram-бота."""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Номери"), KeyboardButton(text="📅 Перевірити дати")],
            [KeyboardButton(text="📋 Забронювати"), KeyboardButton(text="🍽️ Ресторан")],
            [KeyboardButton(text="📞 Контакти"), KeyboardButton(text="❓ Правила")],
        ],
        resize_keyboard=True,
        persistent=True,
    )


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Порожня клавіатура — статичне меню завжди видно внизу екрану."""
    builder = InlineKeyboardBuilder()
    return builder.as_markup()


def room_nav_keyboard(room_index: int, total: int, room_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    nav_buttons = []
    if room_index > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="← Попередній", callback_data="room_nav:prev")
        )
    if room_index < total - 1:
        nav_buttons.append(
            InlineKeyboardButton(text="Наступний →", callback_data="room_nav:next")
        )
    if nav_buttons:
        builder.row(*nav_buttons)
    builder.row(
        InlineKeyboardButton(
            text="📋 Забронювати цей номер",
            callback_data=f"room_nav:book:{room_id}",
        )
    )
    return builder.as_markup()


def room_book_keyboard(room_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📋 Забронювати цей номер",
            callback_data=f"book_room:{room_id}",
        )
    )
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
    return builder.as_markup()


def book_room_keyboard(room_id: int) -> InlineKeyboardMarkup:
    """Single room booking button for availability list."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📋 Забронювати", callback_data=f"book_room:{room_id}")
    )
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


def quick_date_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="+ Сьогодні", callback_data="quick_date:today"),
        InlineKeyboardButton(text="+ Завтра", callback_data="quick_date:tomorrow"),
        InlineKeyboardButton(text="+ Через тиждень", callback_data="quick_date:week"),
    )
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel"))
    return builder.as_markup()


def skip_email_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⏭️ Пропустити", callback_data="skip_email"))
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel"))
    return builder.as_markup()


def quick_guests_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="1", callback_data="quick_guests:1"),
        InlineKeyboardButton(text="2", callback_data="quick_guests:2"),
        InlineKeyboardButton(text="3", callback_data="quick_guests:3"),
        InlineKeyboardButton(text="4", callback_data="quick_guests:4"),
    )
    builder.row(
        InlineKeyboardButton(text="5", callback_data="quick_guests:5"),
        InlineKeyboardButton(text="6", callback_data="quick_guests:6"),
    )
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel"))
    return builder.as_markup()


def quick_time_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="12:00", callback_data="quick_time:12:00"),
        InlineKeyboardButton(text="13:00", callback_data="quick_time:13:00"),
        InlineKeyboardButton(text="14:00", callback_data="quick_time:14:00"),
    )
    builder.row(
        InlineKeyboardButton(text="17:00", callback_data="quick_time:17:00"),
        InlineKeyboardButton(text="18:00", callback_data="quick_time:18:00"),
        InlineKeyboardButton(text="19:00", callback_data="quick_time:19:00"),
    )
    builder.row(
        InlineKeyboardButton(text="20:00", callback_data="quick_time:20:00"),
        InlineKeyboardButton(text="21:00", callback_data="quick_time:21:00"),
    )
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel"))
    return builder.as_markup()
