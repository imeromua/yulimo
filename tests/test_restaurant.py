"""Тести API-ендпоінтів для ресторану."""

import pytest


def _admin_token(client) -> str:
    import uuid

    email = f"admin_{uuid.uuid4().hex[:6]}@yulimo.ua"
    client.post("/auth/register", json={"email": email, "password": "AdminPass1!"})
    login = client.post("/auth/login", json={"email": email, "password": "AdminPass1!"})
    return login.json()["access_token"]


def test_get_menu_empty(client):
    """Порожнє меню повертає []."""
    resp = client.get("/api/restaurant/menu")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_add_menu_item_requires_auth(client):
    """Додавання страви без токена повертає 401."""
    resp = client.post(
        "/api/restaurant/menu",
        json={"name": "Борщ", "category": "soups", "price": 120.0},
    )
    assert resp.status_code == 401


def test_add_and_list_menu_item(client):
    """Адмін може додати страву, вона з'являється у списку меню."""
    token = _admin_token(client)

    create_resp = client.post(
        "/api/restaurant/menu",
        json={
            "name": "Борщ домашній",
            "category": "soups",
            "price": 120.0,
            "weight": "350 г",
            "description": "Традиційний борщ",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_resp.status_code == 201
    data = create_resp.json()
    assert data["name"] == "Борщ домашній"
    assert data["category"] == "soups"
    assert data["price"] == 120.0

    # Страва є у списку
    list_resp = client.get("/api/restaurant/menu")
    assert list_resp.status_code == 200
    names = [item["name"] for item in list_resp.json()]
    assert "Борщ домашній" in names


def test_menu_filter_by_category(client):
    """Фільтр за категорією повертає тільки відповідні страви."""
    token = _admin_token(client)

    client.post(
        "/api/restaurant/menu",
        json={"name": "Шашлик", "category": "grill", "price": 280.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/api/restaurant/menu",
        json={"name": "Борщ", "category": "soups", "price": 100.0},
        headers={"Authorization": f"Bearer {token}"},
    )

    grill_resp = client.get("/api/restaurant/menu?category=grill")
    assert grill_resp.status_code == 200
    for item in grill_resp.json():
        assert item["category"] == "grill"
