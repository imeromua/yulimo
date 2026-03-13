"""Точка входу FastAPI — CORS, middleware, маршрути, обробники помилок."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from core.config import settings
from core.logging_config import error_logger, setup_logging
from middleware.logging_mw import RequestLoggingMiddleware
from middleware.security import SecurityHeadersMiddleware
from routers import admin, auth, bookings, clients, content, emails, media, restaurant, rooms, settings as settings_router
from utils.responses import make_serializable_errors

# ---------------------------------------------------------------------------
# Логування
# ---------------------------------------------------------------------------
setup_logging(debug=settings.DEBUG)
logger = logging.getLogger("yulimo.main")

# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])

# ---------------------------------------------------------------------------
# Застосунок
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description="API для бази відпочинку Юлімо",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.state.limiter = limiter

# ---------------------------------------------------------------------------
# Middleware (порядок важливий: перший підключений виконується останнім)
# ---------------------------------------------------------------------------
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Глобальні обробники помилок
# ---------------------------------------------------------------------------
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_logger.warning("Помилка валідації для %s: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Помилка валідації вхідних даних",
            "details": make_serializable_errors(exc.errors()),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_logger.exception("Необроблена помилка для %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Внутрішня помилка сервера",
            "details": {},
        },
    )


# ---------------------------------------------------------------------------
# Маршрути
# ---------------------------------------------------------------------------
app.include_router(auth.router,            prefix="/auth",           tags=["Автентифікація"])
app.include_router(rooms.router,           prefix="/api/rooms",      tags=["Номери"])
app.include_router(bookings.router,        prefix="/api/bookings",   tags=["Бронювання"])
app.include_router(restaurant.router,      prefix="/api/restaurant", tags=["Ресторан"])
app.include_router(admin.router,           prefix="/api/admin",      tags=["Адмін"])
app.include_router(clients.router,         tags=["Клієнти"])
app.include_router(media.router,           tags=["Медіа"])
app.include_router(emails.router,          tags=["Email"])
app.include_router(content.router,         tags=["Контент"])
app.include_router(settings_router.router, tags=["Налаштування"])


@app.get("/api/health", tags=["Моніторинг"])
def health_check():
    """Перевірка стану сервісу."""
    return {"success": True, "data": {"status": "ok", "project": "Yulimo"}, "message": ""}

