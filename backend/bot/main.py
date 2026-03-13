"""Ініціалізація бота: Bot, Dispatcher, реєстрація вебхука."""

import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage

from core.config import settings

logger = logging.getLogger("yulimo.bot")

bot: Bot | None = None
dp: Dispatcher | None = None

WEBHOOK_PATH = "/api/telegram/webhook"


def _create_storage():
    if settings.REDIS_URL:
        try:
            from redis.asyncio import from_url
            redis_client = from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=False)
            logger.info("Використовуємо RedisStorage для FSM")
            return RedisStorage(redis=redis_client)
        except Exception as exc:
            logger.warning("Не вдалося ініціалізувати RedisStorage: %s — фолбек на MemoryStorage", exc)
    return MemoryStorage()


def _create_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    _bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    _dp = Dispatcher(storage=_create_storage())

    from bot.handlers import start, rooms, availability, booking, restaurant, info

    _dp.include_router(start.router)
    _dp.include_router(rooms.router)
    _dp.include_router(availability.router)
    _dp.include_router(booking.router)
    _dp.include_router(restaurant.router)
    _dp.include_router(info.router)

    return _bot, _dp


async def setup_bot() -> None:
    """Ініціалізує бота та реєструє вебхук."""
    global bot, dp
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.info("TELEGRAM_BOT_TOKEN не задано — бот не запускається")
        return

    try:
        bot, dp = _create_bot_and_dispatcher()
        webhook_url = f"{settings.TELEGRAM_WEBHOOK_BASE_URL.rstrip('/')}{WEBHOOK_PATH}"
        await bot.set_webhook(webhook_url)
        logger.info("Telegram webhook зареєстровано: %s", webhook_url)
    except Exception as exc:
        logger.error("Помилка налаштування Telegram бота: %s", exc)


async def teardown_bot() -> None:
    """Закриває сесію бота."""
    global bot
    if bot is not None:
        try:
            await bot.session.close()
            logger.info("Telegram bot session закрита")
        except Exception as exc:
            logger.error("Помилка закриття сесії бота: %s", exc)
