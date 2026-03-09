"""Підключення до БД: engine з пулом з'єднань, Base, сесія."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import settings

# Аргументи пулу — тільки для PostgreSQL (SQLite не підтримує пул)
_POOL_KWARGS: dict = {}
if not settings.DATABASE_URL.startswith("sqlite"):
    _POOL_KWARGS = {
        "pool_pre_ping": True,
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_recycle": 1800,
    }
else:
    # SQLite: вмикаємо режим WAL для безпечного конкурентного доступу
    _POOL_KWARGS = {"connect_args": {"check_same_thread": False}}

engine = create_engine(settings.DATABASE_URL, **_POOL_KWARGS)

# Для SQLite: вмикаємо підтримку зовнішніх ключів
if settings.DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Залежність FastAPI: забезпечує сесію БД з автоматичним закриттям."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

