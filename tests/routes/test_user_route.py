import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, ANY
from app.routes import user_route

@pytest.mark.usefixtures("client")
class TestUserRoute:

    def test_read_current_user_success(self, client: TestClient):
        # Arrange
        mock_user = MagicMock()
        mock_user.email = "testuser@example.com"

        expected_response = {
            "id": 1,
            "email": "testuser@example.com",
            "full_name": "Test User",
            "created_at": "2025-11-07T21:45:00Z"
        }

        client.app.dependency_overrides[user_route.get_current_user] = lambda: mock_user

        with patch("app.services.user_service.get_user_by_email", return_value=expected_response):
            # Act
            response = client.get("/users/me")

            # Assert
            assert response.status_code == 200
            assert response.json() == expected_response

        client.app.dependency_overrides.clear()

    def test_list_users_success_admin(self, client: TestClient):
        # Arrange
        mock_admin = MagicMock()
        mock_admin.email = "admin@example.com"
        mock_admin.role = "admin"

        expected_users = [
            {"id": 1, "email": "user1@example.com", "full_name": "User One", "created_at": "2025-11-07T21:45:00Z"},
            {"id": 2, "email": "user2@example.com", "full_name": "User Two", "created_at": "2025-11-07T21:46:00Z"}
        ]

        client.app.dependency_overrides[user_route.get_admin_user] = lambda: mock_admin

        with patch("app.services.user_service.list_all_users", return_value=expected_users):
            # Act
            response = client.get("/users/")

            # Assert
            assert response.status_code == 200
            assert response.json() == expected_users

        client.app.dependency_overrides.clear()

    def test_update_current_user_success(self, client: TestClient):
        # Arrange
        mock_user = MagicMock()
        mock_user.email = "testuser@example.com"

        updated_data = {
            "email": "testuser@example.com",  # include email for UserCreate model
            "full_name": "New Name",
            "password": "newpassword123"
        }

        expected_response = {
            "id": 1,
            "email": "testuser@example.com",
            "full_name": "New Name",
            "created_at": "2025-11-07T21:45:00Z"
        }

        client.app.dependency_overrides[user_route.get_current_user] = lambda: mock_user

        with patch("app.services.user_service.update_user", return_value=expected_response):
            # Act
            response = client.put("/users/me", json=updated_data)

            # Assert
            assert response.status_code == 200
            assert response.json() == expected_response

        client.app.dependency_overrides.clear()

    def test_delete_current_user_success(self, client: TestClient):
        # Arrange
        mock_user = MagicMock()
        mock_user.email = "testuser@example.com"

        client.app.dependency_overrides[user_route.get_current_user] = lambda: mock_user

        with patch("app.services.user_service.delete_user") as mock_delete:
            # Act
            response = client.delete("/users/me")

            # Assert
            assert response.status_code == 200
            assert response.json() == {"detail": "User account deleted successfully."}
            mock_delete.assert_called_once_with(db=ANY, user=mock_user)

        client.app.dependency_overrides.clear()
