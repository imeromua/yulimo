"""Спільні фікстури для тестів."""

import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Додаємо backend до PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# SQLite файловий для тестів (між session-scope та function-scope fixtures)
SQLITE_URL = "sqlite:///./test_yulimo.db"

# Встановлюємо до імпорту main, щоб Settings зчитали правильний URL
os.environ.setdefault("DATABASE_URL", SQLITE_URL)
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests-only")
os.environ.setdefault("DEBUG", "True")


@pytest.fixture(scope="session")
def db_engine():
    from database import Base  # noqa: F401 – імпортує моделі через Base

    # Завантажуємо всі моделі, щоб Base знав таблиці
    import models.booking  # noqa: F401
    import models.client  # noqa: F401
    import models.content_block  # noqa: F401
    import models.email_log  # noqa: F401
    import models.email_template  # noqa: F401
    import models.media  # noqa: F401
    import models.restaurant  # noqa: F401
    import models.room  # noqa: F401
    import models.settings  # noqa: F401
    import models.user  # noqa: F401

    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """Кожен тест отримує ізольовану сесію з rollback після завершення."""
    connection = db_engine.connect()
    transaction = connection.begin()
    TestSession = sessionmaker(bind=connection)
    session = TestSession()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """TestClient з перевизначеною залежністю get_db."""
    from database import get_db
    from main import app

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()
