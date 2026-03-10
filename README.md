# 🌲 Юлімо — База відпочинку

> Пуща-Водиця, Київ · [yulimo.kyiv.ua](https://yulimo.kyiv.ua)

## Стек технологій

| Компонент  | Технологія                        |
|------------|-----------------------------------|
| Backend    | Python 3.11 · FastAPI · SQLAlchemy 2 |
| База даних | PostgreSQL 16                     |
| Автент.    | JWT (python-jose) · bcrypt         |
| Frontend   | HTML5 · CSS3 · Vanilla JS (ESM)   |
| Сервер     | Nginx + Ubuntu (systemd)          |
| Docker     | Docker Compose                    |

---

## Структура проєкту

```
yulimo/
├── backend/
│   ├── main.py                # Точка входу FastAPI
│   ├── database.py            # Engine з пулом з'єднань
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── .env.example
│   ├── core/
│   │   ├── config.py          # Pydantic Settings
│   │   ├── security.py        # JWT + bcrypt
│   │   └── logging_config.py  # Структуроване логування
│   ├── models/
│   │   ├── room.py
│   │   ├── booking.py
│   │   ├── restaurant.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── common.py          # Стандартна відповідь
│   │   ├── auth.py
│   │   ├── booking.py
│   │   ├── room.py
│   │   ├── restaurant.py
│   │   └── user.py
│   ├── routers/
│   │   ├── auth.py            # POST /auth/login|register|refresh
│   │   ├── rooms.py
│   │   ├── bookings.py
│   │   ├── restaurant.py
│   │   └── admin.py           # Захищені адмін-ендпоінти
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── booking_service.py # Логіка + SELECT FOR UPDATE
│   │   ├── room_service.py
│   │   └── restaurant_service.py
│   ├── dependencies/
│   │   └── auth.py            # get_current_user, require_admin
│   ├── middleware/
│   │   ├── security.py        # Заголовки безпеки
│   │   └── logging_mw.py      # Логування запитів
│   └── utils/
│       └── responses.py       # success_response / error_response
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   ├── js/
│   │   ├── main.js            # Точка входу (ES module)
│   │   ├── api.js             # Fetch-обгортки
│   │   ├── booking.js         # Логіка форми бронювання
│   │   ├── ui.js              # Навігація, анімації
│   │   └── utils.js           # Утиліти
│   ├── robots.txt
│   └── sitemap.xml
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_bookings.py
│   └── test_rooms.py
├── deploy/
│   ├── setup.sh
│   └── yulimo.service
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## Запуск локально

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # заповни своїми даними
uvicorn main:app --reload --port 8001
```

Swagger UI (тільки у режимі DEBUG=True): http://localhost:8001/docs

---

## Запуск через Docker

```bash
# Скопіювати та налаштувати змінні оточення
cp backend/.env.example backend/.env

# Запустити сервіси
docker compose up --build

# Бекенд доступний на: http://localhost:8001
```

---

## Змінні оточення (`backend/.env`)

| Змінна                     | Опис                                        | За замовчуванням          |
|----------------------------|---------------------------------------------|---------------------------|
| `DATABASE_URL`             | PostgreSQL рядок підключення                | —                         |
| `DB_POOL_SIZE`             | Розмір пулу з'єднань                        | `10`                      |
| `DB_MAX_OVERFLOW`          | Додаткові з'єднання понад пул               | `20`                      |
| `SECRET_KEY`               | Секретний ключ JWT (≥32 символи)            | —                         |
| `ALGORITHM`                | Алгоритм підпису JWT                        | `HS256`                   |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Час дії access-токена                   | `60`                      |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | Час дії refresh-токена                  | `7`                       |
| `ADMIN_EMAIL`              | Email адміністратора за замовчуванням       | —                         |
| `ADMIN_PASSWORD`           | Пароль адміністратора за замовчуванням      | —                         |
| `ALLOWED_ORIGINS`          | Дозволені CORS origins (через кому)         | —                         |
| `RATE_LIMIT_PER_MINUTE`    | Ліміт запитів з однієї IP за хвилину        | `60`                      |
| `DEBUG`                    | Режим налагодження (вмикає /docs)           | `False`                   |
| `LOG_DIR`                  | Директорія для файлів логів                 | `logs`                    |

---

## API-ендпоінти

### Автентифікація

| Метод  | URL               | Опис                        |
|--------|-------------------|-----------------------------|
| `POST` | `/auth/register`  | Реєстрація адміністратора   |
| `POST` | `/auth/login`     | Вхід, отримання JWT-токенів |
| `POST` | `/auth/refresh`   | Оновлення access-токена     |

### Номери

| Метод  | URL                  | Захист | Опис               |
|--------|----------------------|--------|--------------------|
| `GET`  | `/api/rooms/`        | —      | Список номерів     |
| `GET`  | `/api/rooms/{id}`    | —      | Деталі номеру      |
| `POST` | `/api/rooms/`        | Admin  | Створити номер     |

### Бронювання

| Метод  | URL                                  | Захист | Опис                        |
|--------|--------------------------------------|--------|-----------------------------|
| `POST` | `/api/bookings/`                     | —      | Нове бронювання             |
| `GET`  | `/api/bookings/check-availability`   | —      | Перевірити доступність      |

### Ресторан

| Метод  | URL                           | Захист | Опис                     |
|--------|-------------------------------|--------|--------------------------|
| `GET`  | `/api/restaurant/menu`        | —      | Меню ресторану           |
| `POST` | `/api/restaurant/reserve-table` | —    | Резервація столика       |

### Адмін (потребує Bearer-токен)

| Метод   | URL                                      | Опис                           |
|---------|------------------------------------------|--------------------------------|
| `GET`   | `/api/admin/bookings`                    | Усі бронювання                 |
| `PATCH` | `/api/admin/bookings/{id}/status`        | Змінити статус бронювання      |
| `GET`   | `/api/admin/table-reservations`          | Усі резервації столиків        |

### Моніторинг

| Метод | URL            | Опис                    |
|-------|----------------|-------------------------|
| `GET` | `/api/health`  | Перевірка стану сервісу |

### Стандартна відповідь API

```json
// Успіх
{ "success": true, "data": { ... }, "message": "" }

// Помилка
{ "success": false, "error": "опис помилки", "details": {} }
```

---

## Тести

```bash
# Запуск всіх тестів
pytest tests/ -v

# Тільки певна група
pytest tests/test_auth.py -v
pytest tests/test_bookings.py -v
```

Тести використовують SQLite in-memory — PostgreSQL не потрібен.

---

## Міграції бази даних

```bash
cd backend
alembic upgrade head
```

---

## Якість коду

```bash
pip install black isort flake8

# Автоформатування
black backend/
isort backend/

# Перевірка стилю
flake8 backend/ --max-line-length=100
```

---

## Деплой на VPS

```bash
bash deploy/setup.sh
```

Uvicorn слухає на `127.0.0.1:8001`, Nginx проксіює зовнішній трафік.

---

## Безпека

- **JWT** автентифікація з access/refresh токенами
- **bcrypt** хешування паролів
- **Rate limiting** — обмеження кількості запитів (slowapi)
- **Security headers** — CSP, X-Frame-Options, HSTS, X-Content-Type-Options
- **SELECT FOR UPDATE** — захист від гонки станів при бронюванні
- **Валідація вхідних даних** через Pydantic з обмеженнями полів
- **Структуровані відповіді помилок** без витоку внутрішніх деталей
