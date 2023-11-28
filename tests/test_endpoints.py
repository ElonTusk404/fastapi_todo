import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.anyio
async def test_read_root(client: AsyncClient):  # Используем фикстуру client
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Real-Time Task Manager API"}

@pytest.mark.anyio
async def test_create_user(client: AsyncClient):  # Используем фикстуру client
    response = await client.post("/api/v1/register/", json={"username": "test", "password": "test", "email": "test@test.com"})
    assert response.status_code == 201
    assert "id" in response.json()
    assert "username" in response.json()
    assert "email" in response.json()

@pytest.mark.anyio
async def test_login(client: AsyncClient):  # Используем фикстуру client
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    response = await client.post("/api/v1/login/", data={"username": "test", "password": "test"}, headers=headers)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json().get("token_type") == "Bearer"
