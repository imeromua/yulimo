"""Тести системи автентифікації."""

import pytest


def test_register_new_user(client):
    """Успішна реєстрація нового користувача."""
    resp = client.post(
        "/auth/register",
        json={"email": "test@yulimo.ua", "password": "StrongPass123!", "name": "Тест"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client):
    """Реєстрація з існуючим email повертає 409."""
    payload = {"email": "dup@yulimo.ua", "password": "Pass123!", "name": "Дубль"}
    client.post("/auth/register", json=payload)
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 409


def test_login_success(client):
    """Успішний вхід повертає токени."""
    email, password = "login@yulimo.ua", "LoginPass1!"
    client.post("/auth/register", json={"email": email, "password": password})

    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(client):
    """Невірний пароль повертає 401."""
    email = "wrong@yulimo.ua"
    client.post("/auth/register", json={"email": email, "password": "GoodPass1!"})

    resp = client.post("/auth/login", json={"email": email, "password": "WrongPass!"})
    assert resp.status_code == 401


def test_login_nonexistent_user(client):
    """Вхід неіснуючого користувача повертає 401."""
    resp = client.post(
        "/auth/login",
        json={"email": "nobody@yulimo.ua", "password": "SomePass1!"},
    )
    assert resp.status_code == 401


def test_refresh_token(client):
    """Оновлення access-токена за допомогою refresh-токена."""
    email, password = "refresh@yulimo.ua", "RefPass123!"
    client.post("/auth/register", json={"email": email, "password": password})
    login_resp = client.post("/auth/login", json={"email": email, "password": password})
    refresh_token = login_resp.json()["refresh_token"]

    resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_refresh_invalid_token(client):
    """Недійсний refresh-токен повертає 401."""
    resp = client.post("/auth/refresh", json={"refresh_token": "invalid.token.here"})
    assert resp.status_code == 401


def test_admin_route_requires_auth(client):
    """Адмін-маршрути без токена повертають 401."""
    resp = client.get("/api/admin/bookings")
    assert resp.status_code == 401


def test_admin_route_with_valid_token(client):
    """Адмін-маршрути з валідним токеном повертають 200."""
    email, password = "admin@yulimo.ua", "AdminPass1!"
    client.post("/auth/register", json={"email": email, "password": password})
    login = client.post("/auth/login", json={"email": email, "password": password})
    token = login.json()["access_token"]

    resp = client.get("/api/admin/bookings", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
