import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

@pytest.mark.usefixtures("client")
class TestAuthRoute:

    def test_register_user_success(self, client: TestClient):
        # Arrange
        user_data = {
            "email": "testuser@example.com",
            "password": "securepassword123",
            "full_name": "Test User"
        }

        expected_response = {
            "id": 1,
            "email": user_data["email"],
            "full_name": user_data["full_name"],
            "created_at": "2025-11-07T21:45:00Z"
        }

        # Act
        with patch("app.services.auth_service.register_user", return_value=expected_response):
            response = client.post("/auth/register", json=user_data)

        # Assert
        assert response.status_code == 201
        assert response.json() == expected_response

    def test_login_user_success(self, client: TestClient):
        # Arrange
        user_data = {
            "email": "testuser@example.com",
            "password": "securepassword123"
        }

        expected_tokens = {
            "access_token": "fake_access_token",
            "refresh_token": "fake_refresh_token",
            "token_type": "bearer"
        }

        # Act
        with patch("app.services.auth_service.login_user", return_value=expected_tokens):
            response = client.post("/auth/login", json=user_data)

        # Assert
        assert response.status_code == 200
        assert response.json() == expected_tokens

    def test_refresh_token_success(self, client: TestClient):
        # Arrange
        refresh_request = {
            "refresh_token": "fake_refresh_token"
        }

        expected_tokens = {
            "access_token": "new_fake_access_token",
            "refresh_token": "new_fake_refresh_token",
            "token_type": "bearer"
        }

        # Act
        with patch("app.services.auth_service.refresh_tokens", return_value=expected_tokens):
            response = client.post("/auth/refresh", json=refresh_request)

        # Assert
        assert response.status_code == 200
        assert response.json() == expected_tokens

    def test_login_user_missing_password(self, client: TestClient):
        # Arrange
        user_data = {
            "email": "testuser@example.com"
        }

        # Act
        response = client.post("/auth/login", json=user_data)

        # Assert
        assert response.status_code == 422

    def test_register_invalid_email(self, client: TestClient):
        # Arrange
        user_data = {
            "email": "invalidemail",
            "password": "securepassword123",
            "full_name": "Test User"
        }

        # Act
        response = client.post("/auth/register", json=user_data)

        # Assert
        assert response.status_code == 422
