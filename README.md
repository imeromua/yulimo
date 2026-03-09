# 🌲 Yulimo — База відпочинку

> Пуща-Водиця, Київ · [yulimo.kyiv.ua](https://yulimo.kyiv.ua)

## Стек
- **Backend:** Python FastAPI + SQLAlchemy + Alembic
- **БД:** PostgreSQL 16
- **Frontend:** HTML / CSS / Vanilla JS (SPA)
- **Сервер:** Nginx + Ubuntu (systemd-сервіс)
- **DNS/CDN:** Cloudflare

## Структура проєкту
```
yulimo/
├── backend/
│   ├── main.py              # Точка входу FastAPI, CORS, роутери
│   ├── database.py          # SQLAlchemy engine / session / Base
│   ├── requirements.txt     # Python-залежності
│   ├── alembic.ini          # Конфіг міграцій
│   ├── .env.example         # Шаблон змінних оточення
│   ├── models/
│   │   ├── room.py          # Модель Room
│   │   ├── booking.py       # Модель Booking + BookingStatus enum
│   │   ├── restaurant.py    # Моделі MenuItem, TableReservation
│   │   └── user.py          # Модель User
│   ├── schemas/
│   │   ├── room.py          # Pydantic-схеми для номерів
│   │   └── booking.py       # Pydantic-схеми для бронювань
│   └── routers/
│       ├── rooms.py         # GET /api/rooms, POST /api/rooms
│       ├── bookings.py      # POST /api/bookings, GET /api/bookings/check-availability
│       ├── restaurant.py    # GET /api/restaurant/menu, POST /api/restaurant/reserve-table
│       └── admin.py         # GET/PATCH /api/admin/bookings, GET /api/admin/table-reservations
├── frontend/
│   ├── index.html           # Одно-сторінковий сайт (SPA)
│   ├── css/style.css        # Стилі
│   ├── js/main.js           # JS-логіка (бронювання, меню, анімації)
│   ├── robots.txt           # SEO: дозволи для краулерів + посилання на sitemap
│   ├── sitemap.xml          # XML-карта сайту (8 секцій)
│   ├── site.webmanifest     # PWA-маніфест
│   └── favicon-*.png / *.ico
├── deploy/
│   ├── setup.sh             # Скрипт деплою на VPS
│   └── yulimo.service       # systemd-юніт для uvicorn
└── README.md
```

## API-ендпоінти

| Метод | URL | Опис |
|-------|-----|------|
| `GET` | `/api/health` | Перевірка стану сервісу |
| `GET` | `/api/rooms` | Список активних номерів |
| `GET` | `/api/rooms/{id}` | Деталі номеру |
| `POST` | `/api/rooms` | Створити номер |
| `POST` | `/api/bookings` | Нове бронювання (з перевіркою дат) |
| `GET` | `/api/bookings/check-availability` | Перевірити доступність номеру |
| `GET` | `/api/restaurant/menu` | Меню ресторану (фільтр за категорією) |
| `POST` | `/api/restaurant/reserve-table` | Резервація столика |
| `GET` | `/api/admin/bookings` | Усі бронювання (адмін) |
| `PATCH` | `/api/admin/bookings/{id}/status` | Змінити статус бронювання |
| `GET` | `/api/admin/table-reservations` | Усі резервації столиків |

Інтерактивна документація: `http://localhost:8001/docs`

## Змінні оточення (`backend/.env`)

| Змінна | Опис |
|--------|------|
| `DATABASE_URL` | URL підключення до PostgreSQL |
| `SECRET_KEY` | Секретний ключ для JWT |
| `ALGORITHM` | Алгоритм підпису токенів (за замовчуванням `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Час життя токена |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Облікові дані адміністратора |
| `ALLOWED_ORIGINS` | CORS: дозволені origins, через кому |

## Запуск локально
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # заповни своїми даними
uvicorn main:app --reload --port 8001
```
Swagger UI: http://localhost:8001/docs

## Міграції бази даних
```bash
cd backend
alembic upgrade head
```

## Деплой на VPS
```bash
bash deploy/setup.sh
```
Скрипт:
1. Виконує `git pull`
2. Встановлює Python-залежності у `venv`
3. Копіює `yulimo.service` у `/etc/systemd/system/`
4. Вмикає та перезапускає systemd-сервіс
5. Перезавантажує Nginx

Uvicorn слухає на `127.0.0.1:8001`, Nginx проксіює зовнішній трафік.

## Фронтенд — секції сайту
| Секція | Анкор |
|--------|-------|
| Головна | `#` |
| Про нас | `#about` |
| Номери | `#rooms` |
| Ресторан | `#restaurant` |
| Меню | `#menu` |
| Послуги | `#services` |
| Бронювання | `#booking` |
| Контакти | `#contacts` |
