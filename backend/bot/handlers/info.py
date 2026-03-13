"""Обробник інформаційних розділів: Контакти та Правила."""

import logging

from aiogram import Router
from aiogram.types import CallbackQuery

from bot.keyboards import back_to_menu_keyboard

logger = logging.getLogger("yulimo.bot")

router = Router()

CONTACTS_TEXT = (
    "📞 <b>Контакти бази відпочинку Юлімо</b>\n\n"
    "📍 Адреса: Пуща-Водиця, Київ\n"
    "📱 Телефон: +38 (073) 537-60-37\n"
    "📧 Email: info@yulimo.kyiv.ua\n"
    "🌐 Сайт: https://yulimo.kyiv.ua\n"
    "📸 Instagram: @yulimo.kyiv.ua"
)

RULES_TEXT = (
    "❓ <b>Правила відвідування бази Юлімо</b>\n\n"
    "🕑 Час заїзду: з 14:00\n"
    "🕛 Виїзд: до 12:00\n"
    "🌙 Тихий час: з 23:00 до 8:00\n"
    "🚬 Паління лише у відведених місцях\n"
    "🐾 Домашні тварини — за погодженням\n\n"
    "📄 Повні правила: https://yulimo.kyiv.ua/pages/rules.html"
)


@router.callback_query(lambda c: c.data == "menu:contacts")
async def cb_contacts(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        CONTACTS_TEXT,
        parse_mode="HTML",
        reply_markup=back_to_menu_keyboard(),
        disable_web_page_preview=True,
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "menu:rules")
async def cb_rules(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        RULES_TEXT,
        parse_mode="HTML",
        reply_markup=back_to_menu_keyboard(),
        disable_web_page_preview=True,
    )
    await callback.answer()
