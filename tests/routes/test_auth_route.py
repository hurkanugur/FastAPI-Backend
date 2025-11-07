from fastapi.testclient import TestClient
from app.schemas.user_schema import UserInfo, Token

def test_register_user(client: TestClient):
    payload = {"email": "newuser@example.com", "password": "secret123", "full_name": "New User"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data: UserInfo = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "created_at" in data

def test_login_user(client: TestClient, test_user):
    payload = {"email": test_user.email, "password": "testpassword"}
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200
    data: Token = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client: TestClient, test_user):
    payload = {"email": test_user.email, "password": "wrongpassword"}
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 401

def test_refresh_token(client: TestClient, test_user):
    # First login to get refresh token
    login_resp = client.post("/auth/login", json={"email": test_user.email, "password": "testpassword"})
    refresh_token = login_resp.json()["refresh_token"]

    # Call refresh endpoint
    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    data: Token = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
