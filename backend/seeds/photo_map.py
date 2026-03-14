"""Словник фотографій для типів номерів та загальної галереї.

Ключі:
  "standard" — стандартні номери
  "suite"    — номери люкс
  "cottage"  — котеджі
  "gallery"  — загальна галерея (басейн, гриль, ресторан, рибалка, сауна, ліс)

Значення — список імен файлів відносно /images/ (без шляху і без URL-encode).
URL-encode застосовується при виводі: encodeURIComponent() на фронтенді
та urllib.parse.quote() у Python-коді.
"""

PHOTO_MAP: dict[str, list[str]] = {
    "standard": [
        "nomer standart2.jpg",
        "nomer standart5.jpg",
        "nomer standart6.jpg",
        "standart nomer.jpg",
    ],
    "suite": [
        "nomer lyuks.jpg",
        "nomer lyuks2.jpg",
        "nomer-lyuks.jpg",
        "nomer lyuks-11.jpg",
        "nomer lyuks-12.jpg",
        "nomer lyuks-13.jpg",
        "nomer lyuks-14.jpg",
    ],
    "cottage": [
        "kotedzh.jpg",
        "kotedzh2.jpg",
        "kotedzh3.jpg",
        "kotedzh4.jpg",
        "kotedzh5.jpg",
        "kotedzh8-08.jpg",
        "kotedzh8-09.jpg",
        "kotedzh8-10.jpg",
    ],
    "gallery": [
        "baseyn.jpg",
        "baseyn2.jpg",
        "baseyn3.jpg",
        "baseyn4.jpg",
        "hryl zona.jpg",
        "hryl zona2.jpg",
        "hryl zona3.jpg",
        "hryl-zona.jpg",
        "restoran.jpg",
        "restoran-15.jpg",
        "restoran-16.jpg",
        "restoran-17.jpg",
        "restoran-18.jpg",
        "restoran-19.jpg",
        "restoran-20.jpg",
        "rybalka.jpg",
        "rybalka2.jpg",
        "rybalka3.jpg",
        "sauna-banya-21.jpg",
        "sauna-banya-22.jpg",
        "sauna-banya-23.jpg",
        "sauna-banya-24.jpg",
        "sauna-banya-25.jpg",
        "lis.jpg",
        "lis2.jpg",
    ],
}
