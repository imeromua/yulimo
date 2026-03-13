"""Маршрут для вебхука Telegram."""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("yulimo.bot")

router = APIRouter()


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request) -> JSONResponse:
    """Приймає оновлення від Telegram і передає їх диспетчеру."""
    from bot.main import bot, dp

    if bot is None or dp is None:
        logger.warning("Telegram webhook отримав запит, але бот не ініціалізований")
        return JSONResponse({"ok": False, "error": "Bot not initialized"}, status_code=503)

    try:
        from aiogram.types import Update

        data = await request.json()
        update = Update(**data)
        await dp.feed_update(bot, update)
    except Exception as exc:
        logger.error("Помилка обробки Telegram update: %s", exc)

    return JSONResponse({"ok": True})
