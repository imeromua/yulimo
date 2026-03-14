"""Скрипт оновлення фотографій у БД для активних номерів.

Для кожного активного номера встановлює поле photos відповідно до типу
номера, використовуючи словник PHOTO_MAP з photo_map.py.

Запуск:
    python backend/seeds/update_photos.py
"""

import sys
import os

# Додаємо корінь backend до шляху, щоб знайти database.py і моделі
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal  # noqa: E402
from models.room import Room  # noqa: E402
from seeds.photo_map import PHOTO_MAP  # noqa: E402


def update_photos() -> None:
    db = SessionLocal()
    try:
        rooms = db.query(Room).filter(Room.is_active == True).all()  # noqa: E712

        if not rooms:
            print("Активних номерів не знайдено.")
            return

        updated = 0
        skipped = 0

        for room in rooms:
            photos = PHOTO_MAP.get(room.type)
            if photos is None:
                print(f"  [ПРОПУЩЕНО] id={room.id} name={room.name!r} — невідомий тип {room.type!r}")
                skipped += 1
                continue

            room.photos = photos
            print(f"  [ОНОВЛЕНО]  id={room.id} name={room.name!r} type={room.type!r} → {len(photos)} фото")
            updated += 1

        db.commit()
        print(f"\nГотово: оновлено {updated}, пропущено {skipped}.")
    finally:
        db.close()


if __name__ == "__main__":
    update_photos()
