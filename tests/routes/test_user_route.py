from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.schemas.user_schema import UserInfo, UserCreate

client = TestClient(app)

# Dummy user data
dummy_user = UserInfo(
    id=1,
    email="test@example.com",
    full_name="Test User",
    created_at="2025-11-07T12:00:00"
)

dummy_user_create = UserCreate(
    email="test@example.com",
    password="securepassword",
    full_name="Test User"
)


@patch("app.services.user_service.get_user_by_email")
@patch("app.core.dependencies.get_current_user")
def test_read_current_user(mock_current_user, mock_get_user_by_email):
    mock_current_user.return_value = MagicMock(email="test@example.com")
    mock_get_user_by_email.return_value = dummy_user

    response = client.get("/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == dummy_user.email
    assert data["full_name"] == dummy_user.full_name


@patch("app.services.user_service.list_all_users")
@patch("app.core.dependencies.get_admin_user")
def test_list_users(mock_get_admin, mock_list_all_users):
    mock_get_admin.return_value = MagicMock(email="admin@example.com")
    mock_list_all_users.return_value = [dummy_user]

    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["email"] == dummy_user.email


@patch("app.services.user_service.update_user_profile")
@patch("app.core.dependencies.get_current_user")
def test_update_current_user(mock_current_user, mock_update_user):
    mock_current_user.return_value = MagicMock(email="test@example.com")
    mock_update_user.return_value = dummy_user

    payload = {
        "email": "test@example.com",
        "password": "newpassword",
        "full_name": "Updated User"
    }
    response = client.put("/users/me", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == dummy_user.full_name
