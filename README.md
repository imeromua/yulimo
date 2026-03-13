# 🌲 Юлімо — База відпочинку

> Пуща-Водиця, Київ · [yulimo.kyiv.ua](https://yulimo.kyiv.ua) · [@yulimo_bot](https://t.me/yulimo_bot)

Повноцінний веб-сайт і Telegram-бот для бази відпочинку: бронювання номерів, резервація столиків ресторану, адміністративна панель.

---

## Стек технологій

| Компонент | Технологія |
|---|---|
| Backend | Python 3.11 · FastAPI · SQLAlchemy 2 |
| База даних | PostgreSQL 16 |
| Кеш / FSM | Redis 7 |
| Автент. | JWT (python-jose) · bcrypt |
| Frontend | HTML5 · CSS3 · Vanilla JS (ESM) |
| Telegram | aiogram 3.7 · Webhook · RedisStorage |
| Сервер | Nginx · Ubuntu · systemd |

---

## Структура проєкту

```
yulimo/
├── backend/
│   ├── main.py                  # Точка входу FastAPI
│   ├── database.py              # Engine з пулом з'єднань
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── .env.example
│   ├── core/
│   │   ├── config.py              # Pydantic Settings
│   │   ├── security.py            # JWT + bcrypt
│   │   └── logging_config.py      # Структуроване логування
│   ├── models/
│   │   ├── room.py                # Номери (photos: JSON)
│   │   ├── booking.py
│   │   ├── restaurant.py
│   │   └── user.py
│   ├── schemas/
│   ├── routers/
│   │   ├── auth.py
│   │   ├── rooms.py
│   │   ├── bookings.py
│   │   ├── restaurant.py
│   │   └── admin.py
│   ├── services/
│   ├── middleware/
│   ├── dependencies/
│   ├── utils/
│   └── bot/
│       ├── main.py                # Bot + Dispatcher + RedisStorage
│       ├── cache.py               # Redis-кеш номерів
│       ├── keyboards.py           # ReplyKeyboard + InlineKeyboard
│       ├── states.py              # FSM стейти
│       └── handlers/
│           ├── start.py             # /start, головне меню
│           ├── rooms.py             # Перегляд номерів з фото
│           ├── booking.py           # FSM-флоу бронювання
│           ├── availability.py      # Перевірка дат
│           ├── restaurant.py        # Резервація столика
│           └── info.py              # Контакти, правила
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   ├── js/
│   │   ├── main.js
│   │   ├── api.js
│   │   ├── booking.js
│   │   ├── ui.js
│   │   └── utils.js
│   ├── images/                  # Фото номерів і галерея
│   ├── pages/
│   │   ├── rules.html
│   │   └── privacy.html
│   ├── robots.txt
│   └── sitemap.xml
├── deploy/
│   ├── setup.sh
│   └── yulimo.service
└── README.md
```

---

## Telegram-бот [@yulimo_bot](https://t.me/yulimo_bot)

Бот працює через **Webhook** (не polling). Функціонал:

| Кнопка | Опис |
|---|---|
| 🏠 Номери | Карусель номерів з фото, ціна, зручностями |
| 📋 Забронювати | FSM-флоу бронювання (дати, ім'я, телефон) |
| 📅 Перевірити дати | Доступність номерів на період |
| 🍽️ Ресторан | Резервація столика з вибором дати/часу/гостей |
| 📞 Контакти | Адреса, телефони, email, сайт |
| ❓ Правила | Правила заселення + посилання на сайт |

**Особливості:**
- Статичне `ReplyKeyboard` — завжди видне внизу екрану
- FSM стейти зберігаються в Redis (не втрачаються при рестарті)
- Номери кешуються в Redis на 5 хвилин — швидка навігація без запитів до БД
- Повідомлення адміну в Telegram при новому бронюванні

---

## Змінні оточення (`backend/.env`)

| Змінна | Опис | За замовчуванням |
|---|---|---|
| `DATABASE_URL` | PostgreSQL рядок підключення | — |
| `REDIS_URL` | Redis рядок підключення | `redis://localhost:6379/0` |
| `SECRET_KEY` | Секретний ключ JWT (≥32 символи) | — |
| `ADMIN_EMAIL` | Email адміністратора | — |
| `ADMIN_PASSWORD` | Пароль адміністратора | — |
| `TELEGRAM_BOT_TOKEN` | Токен бота від @BotFather | — |
| `TELEGRAM_ADMIN_CHAT_ID` | Chat ID для повідомлень | — |
| `TELEGRAM_WEBHOOK_BASE_URL` | Базовий URL сайту | `https://yulimo.kyiv.ua` |
| `RESEND_API_KEY` | API ключ Resend для email | — |
| `ALLOWED_ORIGINS` | CORS origins (через кому) | — |
| `DEBUG` | Режим налагодження (вмикає /docs) | `False` |
| `RATE_LIMIT_PER_MINUTE` | Ліміт запитів з однієї IP | `60` |

---

## Запуск локально

```bash
# 1. Віртуальне оточення
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Налаштування
cp .env.example .env
# відредагуйте .env

# 3. Міграція БД
alembic upgrade head

# 4. Запуск
uvicorn main:app --reload --port 8001
```

Swagger UI (тільки при `DEBUG=True`): http://localhost:8001/docs

> **Telegram-бот локально** потребує публічного HTTPS URL. Використовуйте [ngrok](https://ngrok.com) і вкажіть `TELEGRAM_WEBHOOK_BASE_URL=https://xxxx.ngrok.io`

---

## API-ендпоінти

### Автентифікація

| Метод | URL | Опис |
|---|---|---|
| `POST` | `/auth/login` | Вхід, отримання JWT-токенів |
| `POST` | `/auth/refresh` | Оновлення access-токена |

### Номери

| Метод | URL | Захист | Опис |
|---|---|---|---|
| `GET` | `/api/rooms/` | — | Список активних номерів |
| `GET` | `/api/rooms/{id}` | — | Деталі номера |
| `POST` | `/api/rooms/` | Admin | Створити номер |
| `PATCH` | `/api/rooms/{id}` | Admin | Оновити номер |

### Бронювання

| Метод | URL | Захист | Опис |
|---|---|---|---|
| `POST` | `/api/bookings/` | — | Нове бронювання |
| `GET` | `/api/bookings/check-availability` | — | Перевірка доступності |

### Ресторан

| Метод | URL | Опис |
|---|---|---|
| `GET` | `/api/restaurant/menu` | Меню |
| `POST` | `/api/restaurant/reserve-table` | Резервація столика |

### Адмін (Bearer JWT)

| Метод | URL | Опис |
|---|---|---|
| `GET` | `/api/admin/bookings` | Усі бронювання |
| `PATCH` | `/api/admin/bookings/{id}/status` | Змінити статус |
| `GET` | `/api/admin/table-reservations` | Усі резервації |
| `GET` | `/api/settings` | Налаштування сайту |
| `PATCH` | `/api/settings` | Оновити налаштування |

### Telegram Webhook

| Метод | URL | Опис |
|---|---|---|
| `POST` | `/api/telegram/webhook` | Обробка подій бота |

### Моніторинг

| Метод | URL | Опис |
|---|---|---|
| `GET` | `/api/health` | Перевірка стану сервісу |

---

## Деплой на VPS

```bash
# Пулл змін
git pull

# Інсталяція залежностей
cd backend && source ../venv/bin/activate
pip install -r requirements.txt

# Міграції
alembic upgrade head

# Перезапуск
sudo systemctl restart yulimo
```

Uvicorn слухає на `127.0.0.1:8001`, Nginx проксіює зовнішній трафік + Cloudflare SSL.

---

## Тести

```bash
cd backend && source ../venv/bin/activate
pytest tests/ -v
```

Тести використовують SQLite in-memory — PostgreSQL не потрібен.

---

## Безпека

- **JWT** автентифікація з access/refresh токенами
- **bcrypt** хешування паролів
- **Rate limiting** — slowapi, 60 зап/хв з однієї IP
- **Security headers** — CSP, HSTS, X-Frame-Options
- **SELECT FOR UPDATE** — захист від гонки станів при бронюванні
- **Pydantic** валідація всіх вхідних даних
