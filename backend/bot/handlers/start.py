"""Обробник /start та головного меню."""

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import main_menu_keyboard

logger = logging.getLogger("yulimo.bot")

router = Router()

WELCOME_TEXT = (
    "🌲 Ласкаво просимо до бази відпочинку Юлімо!\n"
    "Оберіть потрібний розділ:"
)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "❌ Дію скасовано.\n\n" + WELCOME_TEXT,
        reply_markup=main_menu_keyboard(),
    )


# ── Reply keyboard text handlers ──────────────────────────────────────────────

@router.message(F.text == "🏠 Номери")
async def text_rooms(message: Message, state: FSMContext) -> None:
    from bot.handlers.rooms import show_rooms
    await show_rooms(message, state)


@router.message(F.text == "📅 Перевірити дати")
async def text_availability(message: Message, state: FSMContext) -> None:
    from bot.keyboards import cancel_keyboard
    from bot.states import AvailabilityStates
    await state.set_state(AvailabilityStates.enter_checkin)
    await message.answer(
        "📅 Введіть дату заїзду (формат: ДД.ММ.РРРР):",
        reply_markup=cancel_keyboard(),
    )


@router.message(F.text == "📋 Забронювати")
async def text_booking(message: Message, state: FSMContext) -> None:
    from bot.keyboards import back_to_menu_keyboard, rooms_list_keyboard
    from bot.states import BookingStates
    from database import SessionLocal
    from services import room_service

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
        await message.answer(
            "😔 На жаль, наразі немає доступних номерів.",
            reply_markup=back_to_menu_keyboard(),
        )
        return

    await state.set_state(BookingStates.select_room)
    await message.answer(
        "🏠 Оберіть номер для бронювання:",
        reply_markup=rooms_list_keyboard(rooms),
    )


@router.message(F.text == "🍽️ Ресторан")
async def text_restaurant(message: Message, state: FSMContext) -> None:
    from bot.keyboards import quick_date_keyboard
    from bot.states import TableStates

    await state.clear()
    await state.set_state(TableStates.enter_date)
    await message.answer(
        "🍽️ <b>Резервація столика</b>\n\nВведіть дату (формат: ДД.ММ.РРРР):",
        parse_mode="HTML",
        reply_markup=quick_date_keyboard(),
    )


@router.message(F.text == "📞 Контакти")
async def text_contacts(message: Message) -> None:
    from bot.handlers.info import CONTACTS_TEXT
    from bot.keyboards import back_to_menu_keyboard

    await message.answer(
        CONTACTS_TEXT,
        parse_mode="HTML",
        reply_markup=back_to_menu_keyboard(),
        disable_web_page_preview=True,
    )


@router.message(F.text == "❓ Правила")
async def text_rules(message: Message) -> None:
    from bot.handlers.info import RULES_TEXT
    from bot.keyboards import back_to_menu_keyboard

    await message.answer(
        RULES_TEXT,
        parse_mode="HTML",
        reply_markup=back_to_menu_keyboard(),
        disable_web_page_preview=True,
    )


# ── Callback handlers ─────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "menu:main")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(lambda c: c.data == "cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        "❌ Дію скасовано.\n\n" + WELCOME_TEXT,
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer("❌ Скасовано")
