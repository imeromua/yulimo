"""Тести бронювань: створення, перевірка доступності, запобігання перетину дат."""

import pytest
from datetime import date, timedelta


def _create_room(client, token: str, price: float = 1200.0) -> int:
    """Допоміжна функція: створити кімнату і повернути її ID."""
    resp = client.post(
        "/api/rooms/",
        json={
            "name": "Стандарт",
            "type": "standard",
            "price": price,
            "capacity": 2,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _admin_token(client) -> str:
    """Зареєструвати адміна та повернути access-токен."""
    import uuid

    email = f"admin_{uuid.uuid4().hex[:6]}@yulimo.ua"
    client.post(
        "/auth/register",
        json={"email": email, "password": "AdminPass1!"},
    )
    login = client.post(
        "/auth/login", json={"email": email, "password": "AdminPass1!"}
    )
    return login.json()["access_token"]


def test_create_booking_success(client):
    """Успішне бронювання вільного номеру."""
    token = _admin_token(client)
    room_id = _create_room(client, token)

    check_in = date.today() + timedelta(days=10)
    check_out = check_in + timedelta(days=3)

    resp = client.post(
        "/api/bookings/",
        json={
            "room_id": room_id,
            "guest_name": "Іван Іванов",
            "guest_phone": "+380501234567",
            "check_in": str(check_in),
            "check_out": str(check_out),
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["room_id"] == room_id
    assert data["nights"] == 3
    assert data["total_price"] == 3 * 1200.0
    assert data["status"] == "pending"


def test_create_booking_room_not_found(client):
    """Бронювання неіснуючого номеру повертає 404."""
    check_in = date.today() + timedelta(days=5)
    check_out = check_in + timedelta(days=2)

    resp = client.post(
        "/api/bookings/",
        json={
            "room_id": 99999,
            "guest_name": "Петро",
            "guest_phone": "+380501111111",
            "check_in": str(check_in),
            "check_out": str(check_out),
        },
    )
    assert resp.status_code == 404


def test_overlapping_booking_rejected(client):
    """Бронювання номеру на зайняті дати повертає 409."""
    token = _admin_token(client)
    room_id = _create_room(client, token)

    check_in = date.today() + timedelta(days=20)
    check_out = check_in + timedelta(days=5)

    # Перше бронювання
    r1 = client.post(
        "/api/bookings/",
        json={
            "room_id": room_id,
            "guest_name": "Гість Один",
            "guest_phone": "+380501234567",
            "check_in": str(check_in),
            "check_out": str(check_out),
        },
    )
    assert r1.status_code == 201

    # Друге бронювання на ті ж дати — конфлікт
    r2 = client.post(
        "/api/bookings/",
        json={
            "room_id": room_id,
            "guest_name": "Гість Два",
            "guest_phone": "+380509999999",
            "check_in": str(check_in + timedelta(days=1)),
            "check_out": str(check_out - timedelta(days=1)),
        },
    )
    assert r2.status_code == 409


def test_adjacent_bookings_allowed(client):
    """Бронювання, що починається в день виїзду попереднього — дозволено."""
    token = _admin_token(client)
    room_id = _create_room(client, token)

    check_in_1 = date.today() + timedelta(days=30)
    check_out_1 = check_in_1 + timedelta(days=3)

    client.post(
        "/api/bookings/",
        json={
            "room_id": room_id,
            "guest_name": "Гість А",
            "guest_phone": "+380501111111",
            "check_in": str(check_in_1),
            "check_out": str(check_out_1),
        },
    )

    # Починається рівно в день виїзду → не перетинається
    r2 = client.post(
        "/api/bookings/",
        json={
            "room_id": room_id,
            "guest_name": "Гість Б",
            "guest_phone": "+380502222222",
            "check_in": str(check_out_1),
            "check_out": str(check_out_1 + timedelta(days=2)),
        },
    )
    assert r2.status_code == 201


def test_check_availability_free(client):
    """Перевірка доступності вільного номеру."""
    token = _admin_token(client)
    room_id = _create_room(client, token)

    check_in = date.today() + timedelta(days=40)
    check_out = check_in + timedelta(days=2)

    resp = client.get(
        "/api/bookings/check-availability",
        params={"room_id": room_id, "check_in": str(check_in), "check_out": str(check_out)},
    )
    assert resp.status_code == 200
    assert resp.json()["available"] is True


def test_check_availability_occupied(client):
    """Перевірка доступності зайнятого номеру."""
    token = _admin_token(client)
    room_id = _create_room(client, token)

    check_in = date.today() + timedelta(days=50)
    check_out = check_in + timedelta(days=3)

    # Бронюємо
    client.post(
        "/api/bookings/",
        json={
            "room_id": room_id,
            "guest_name": "Гість В",
            "guest_phone": "+380503333333",
            "check_in": str(check_in),
            "check_out": str(check_out),
        },
    )

    # Перевіряємо той же проміжок
    resp = client.get(
        "/api/bookings/check-availability",
        params={
            "room_id": room_id,
            "check_in": str(check_in + timedelta(days=1)),
            "check_out": str(check_out),
        },
    )
    assert resp.status_code == 200
    assert resp.json()["available"] is False


def test_invalid_dates_validation(client):
    """Дата виїзду раніше дати заїзду відхиляється (422)."""
    check_in = date.today() + timedelta(days=10)
    check_out = check_in - timedelta(days=1)  # Неправильно!

    resp = client.post(
        "/api/bookings/",
        json={
            "room_id": 1,
            "guest_name": "Тест",
            "guest_phone": "+380500000000",
            "check_in": str(check_in),
            "check_out": str(check_out),
        },
    )
    assert resp.status_code == 422


def test_update_booking_status(client):
    """Адмін може змінити статус бронювання."""
    token = _admin_token(client)
    room_id = _create_room(client, token)

    check_in = date.today() + timedelta(days=60)
    check_out = check_in + timedelta(days=2)

    create_resp = client.post(
        "/api/bookings/",
        json={
            "room_id": room_id,
            "guest_name": "Тест Статус",
            "guest_phone": "+380504444444",
            "check_in": str(check_in),
            "check_out": str(check_out),
        },
    )
    booking_id = create_resp.json()["id"]

    patch_resp = client.patch(
        f"/api/admin/bookings/{booking_id}/status",
        params={"status": "confirmed"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["success"] is True
