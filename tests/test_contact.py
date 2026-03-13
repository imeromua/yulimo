"""Тести ендпоінту /api/contact."""

from unittest.mock import AsyncMock, patch


def test_contact_success(client):
    """Форма зворотного зв'язку повертає success:true."""
    with patch(
        "routers.contact.smtp_email_service.send_manual_email",
        new_callable=AsyncMock,
    ):
        resp = client.post(
            "/api/contact",
            json={
                "name": "Іван Тестовий",
                "email": "ivan@test.ua",
                "message": "Тестове повідомлення для перевірки",
            },
        )
    assert resp.status_code == 200
    assert resp.json() == {"success": True}


def test_contact_validation_missing_fields(client):
    """Відправка без обов'язкових полів повертає 422."""
    resp = client.post("/api/contact", json={"name": "Іван"})
    assert resp.status_code == 422


def test_contact_validation_short_message(client):
    """Занадто коротке повідомлення повертає 422."""
    resp = client.post(
        "/api/contact",
        json={"name": "Іван", "email": "ivan@test.ua", "message": "Hi"},
    )
    assert resp.status_code == 422


def test_contact_invalid_email(client):
    """Некоректна email-адреса повертає 422."""
    resp = client.post(
        "/api/contact",
        json={"name": "Іван", "email": "not-an-email", "message": "Тестове повідомлення"},
    )
    assert resp.status_code == 422
