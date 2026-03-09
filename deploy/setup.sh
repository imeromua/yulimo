#!/bin/bash
# Скрипт розгортання Yulimo на VPS

set -e

echo "=== Yulimo Deploy ==="

cd /home/anubis/yulimo

# Оновлюємо код
git pull origin main

# Створюємо venv якщо не існує
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual env created"
fi

# Встановлюємо залежності
./venv/bin/pip install -r backend/requirements.txt

# Копіюємо .env якщо не існує
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo "!!! Заповни backend/.env своїми даними !!!"
fi

# Копіюємо systemd сервіс
sudo cp deploy/yulimo.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable yulimo
sudo systemctl restart yulimo

# Перезапускаємо nginx
sudo systemctl reload nginx

echo "=== Deploy завершено ==="
echo "Статус: sudo systemctl status yulimo"
