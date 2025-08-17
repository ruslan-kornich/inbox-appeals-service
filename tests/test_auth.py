"""
Authentication API tests:
- Register a new user.
- Login with correct credentials.
- Negative scenarios for duplicate registration and invalid login.
"""

import pytest


@pytest.mark.asyncio
async def test_register_and_login_success(client):
    # Register
    register_body = {
        "email": "user1@example.com",
        "password": "Strong123!",
        "inn": "1234567890",
        "phone": "+380501234567",
        "first_name": "Іван",
        "last_name": "Іванов",
        "middle_name": "Петрович",
        "birth_date": "1990-01-01",
    }
    response = await client.post("/auth/register", json=register_body)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == register_body["email"]
    assert data["role"] == "USER"
    assert "id" in data

    # Login
    login_body = {"email": register_body["email"], "password": register_body["password"]}
    response = await client.post("/auth/login", json=login_body)
    assert response.status_code == 200
    token_payload = response.json()
    assert "access_token" in token_payload
    assert token_payload["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_400(client):
    body = {
        "email": "dupe@example.com",
        "password": "Strong123!",
        "inn": "1111111111",
        "phone": "+380671112233",
        "first_name": "Олег",
        "last_name": "Сидоренко",
        "middle_name": "Іванович",
        "birth_date": "1991-05-05",
    }
    first = await client.post("/auth/register", json=body)
    assert first.status_code == 201

    second = await client.post("/auth/register", json=body)
    assert second.status_code == 400
    assert "Email already registered" in second.text


@pytest.mark.asyncio
async def test_login_invalid_credentials_returns_401(client):
    response = await client.post("/auth/login", json={"email": "none@example.com", "password": "badpass"})
    assert response.status_code == 401
