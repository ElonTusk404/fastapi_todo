from fastapi.testclient import TestClient
import asyncio

from main import app

client = TestClient(app)

jwt_token = None

def auth_header():
    global jwt_token
    return {"Authorization": f"Bearer {jwt_token}"}

async def test_read_root():
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Real-Time Task Manager API"}

async def test_create_user():
    response = await client.post("/api/v1/register/", json={"username": "test", "password": "test", "email": "test@test.com"})
    assert response.status_code == 201
    assert "id" in response.json()
    assert "username" in response.json()
    assert "email" in response.json()

async def test_login():
    global jwt_token
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    response = await client.post("/api/v1/login/", data={"username": "test", "password": "test"}, headers=headers)
    jwt_token = response.json().get("access_token")
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json().get("token_type") == "bearer"

async def test_create_task():
    response = await client.post("/api/v1/tasks/", json={"title": "New Task", "description": "some_text"}, headers=auth_header())
    assert response.status_code == 200
    task = response.json()
    assert "id" in task
    assert task["title"] == "New Task"
    assert task["completed"] is False

async def test_read_task():
    task_id = 1
    response = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_header())
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == task_id

async def test_read_invalid_task():
    invalid_task_id = 999
    response = await client.get(f"/api/v1/tasks/{invalid_task_id}", headers=auth_header())
    assert response.status_code == 404
