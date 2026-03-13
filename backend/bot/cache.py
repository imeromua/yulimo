"""Кеш номерів через Redis."""

import json
import logging

import redis.asyncio as aioredis

from core.config import settings

logger = logging.getLogger("yulimo.cache")

ROOMS_KEY = "yulimo:rooms:active"
ROOMS_TTL = 300  # 5 хвилин

_redis: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


async def get_cached_rooms() -> list[dict] | None:
    """Повертає кешований список номерів або None."""
    try:
        r = get_redis()
        data = await r.get(ROOMS_KEY)
        if data:
            return json.loads(data)
    except Exception as exc:
        logger.warning("Помилка читання кешу номерів: %s", exc)
    return None


async def set_cached_rooms(rooms_data: list[dict]) -> None:
    """Зберігає список номерів в Redis на TTL секунд."""
    try:
        r = get_redis()
        await r.set(ROOMS_KEY, json.dumps(rooms_data, ensure_ascii=False), ex=ROOMS_TTL)
    except Exception as exc:
        logger.warning("Помилка запису кешу номерів: %s", exc)


async def invalidate_rooms_cache() -> None:
    """Очищає кеш номерів (наприклад, після редагування через адмінку)."""
    try:
        r = get_redis()
        await r.delete(ROOMS_KEY)
    except Exception as exc:
        logger.warning("Помилка очищення кешу: %s", exc)
