"""Тести API-ендпоінтів для номерів."""

import pytest


def _admin_token(client) -> str:
    import uuid

    email = f"admin_{uuid.uuid4().hex[:6]}@yulimo.ua"
    client.post("/auth/register", json={"email": email, "password": "AdminPass1!"})
    login = client.post("/auth/login", json={"email": email, "password": "AdminPass1!"})
    return login.json()["access_token"]


def test_get_rooms_empty(client):
    """Порожній список номерів повертає []."""
    resp = client.get("/api/rooms/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_create_room_requires_auth(client):
    """Створення номеру без токена повертає 401."""
    resp = client.post(
        "/api/rooms/",
        json={"name": "Тест", "type": "standard", "price": 500.0},
    )
    assert resp.status_code == 401


def test_create_and_get_room(client):
    """Адмін може створити номер, він з'являється у списку."""
    token = _admin_token(client)

    create_resp = client.post(
        "/api/rooms/",
        json={
            "name": "Котедж Сосна",
            "type": "cottage",
            "description": "Затишний котедж",
            "capacity": 4,
            "area": 65.0,
            "price": 2500.0,
            "amenities": ["wifi", "sauna"],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_resp.status_code == 201
    room_id = create_resp.json()["id"]
    assert create_resp.json()["name"] == "Котедж Сосна"

    # Номер є у списку
    list_resp = client.get("/api/rooms/")
    ids = [r["id"] for r in list_resp.json()]
    assert room_id in ids

    # Деталі номеру
    detail_resp = client.get(f"/api/rooms/{room_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["price"] == 2500.0


def test_get_room_not_found(client):
    """Запит неіснуючого номеру повертає 404."""
    resp = client.get("/api/rooms/99999")
    assert resp.status_code == 404


def test_health_check(client):
    """Ендпоінт health повертає status ok."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["status"] == "ok"
