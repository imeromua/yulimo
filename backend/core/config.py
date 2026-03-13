"""Налаштування застосунку через pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Додаток
    APP_NAME: str = "Yulimo API"
    DEBUG: bool = False
    VERSION: str = "2.0.0"

    # База даних
    DATABASE_URL: str = "sqlite:///./yulimo.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30

    # JWT
    SECRET_KEY: str = "change-this-to-a-very-long-random-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Адмін за замовчуванням
    ADMIN_EMAIL: str = "admin@yulimo.kyiv.ua"
    ADMIN_PASSWORD: str = "change-this-password"

    # Email (Resend)
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@yulimo.kyiv.ua"
    NOTIFICATION_ADMIN_EMAIL: str = "info@yulimo.kyiv.ua"

    # Email (SMTP) — legacy, не використовується
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_FROM: str = ""

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,https://yulimo.kyiv.ua"

    # Rate limiting (запитів за хвилину)
    RATE_LIMIT_PER_MINUTE: int = 60

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_ADMIN_CHAT_ID: str = ""
    TELEGRAM_WEBHOOK_BASE_URL: str = "https://yulimo.kyiv.ua"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
