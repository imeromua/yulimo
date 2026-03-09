"""Налаштування структурованого логування."""

import logging
import os
import sys


def setup_logging(debug: bool = False) -> None:
    """Ініціалізує логери для всього застосунку."""
    level = logging.DEBUG if debug else logging.INFO

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    # Основний хендлер — stdout
    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
    ]

    # Файловий хендлер (якщо є доступ до папки logs/)
    logs_dir = os.getenv("LOG_DIR", "logs")
    try:
        os.makedirs(logs_dir, exist_ok=True)
        handlers.append(logging.FileHandler(f"{logs_dir}/app.log", encoding="utf-8"))
    except OSError:
        pass  # Не критично — продовжуємо тільки з stdout

    logging.basicConfig(level=level, format=fmt, datefmt=date_fmt, handlers=handlers)

    # Зменшуємо шум від сторонніх бібліотек
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("passlib").setLevel(logging.WARNING)


# Іменовані логери для різних підсистем
auth_logger = logging.getLogger("yulimo.auth")
booking_logger = logging.getLogger("yulimo.booking")
request_logger = logging.getLogger("yulimo.request")
error_logger = logging.getLogger("yulimo.error")
