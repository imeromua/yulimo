# 🌲 Yulimo — База відпочинку

> Пуща-Водиця, Київ · [yulimo.kyiv.ua](https://yulimo.kyiv.ua)

## Стек
- **Backend:** Python FastAPI + SQLAlchemy
- **БД:** PostgreSQL 16
- **Frontend:** HTML/CSS/JS
- **Сервер:** Nginx + Ubuntu
- **DNS/CDN:** Cloudflare

## Структура
```
yulimo/
├── backend/        # FastAPI додаток
├── frontend/       # HTML/CSS/JS
├── deploy/         # Скрипти деплою та systemd
└── README.md
```

## Запуск локально
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # заповни своїми даними
uvicorn main:app --reload
```
API docs: http://localhost:8000/docs

## Деплой на VPS
```bash
bash deploy/setup.sh
```
