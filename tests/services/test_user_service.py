import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from app.services import user_service
from app.models.user_model import User
from sqlalchemy.orm import Session


@pytest.mark.unit
class TestUserService:

    def test_get_user_by_email_success(self):
        # Arrange
        mock_db = MagicMock(spec=Session)
        user_in_db = User(email="test@example.com", hashed_password="hashed_secret")
        mock_db.query().filter().first.return_value = user_in_db

        # Act
        user = user_service.get_user_by_email(mock_db, "test@example.com")

        # Assert
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_secret"

    def test_get_user_by_email_not_found_raises(self):
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_db.query().filter().first.return_value = None  # User not found

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            user_service.get_user_by_email(mock_db, "nonexistent@example.com")
        assert exc.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc.value.detail == "User not found"

    def test_update_user_success(self):
        # Arrange
        mock_db = MagicMock(spec=Session)
        user_in_db = User(email="test@example.com", full_name="Old Name", hashed_password="hashed_secret")
        mock_db.query().filter().first.return_value = user_in_db
        updated_full_name = "New Name"
        updated_password = "newpassword"

        with patch("app.services.user_service.get_password_hash", return_value="new_hashed_password"):
            # Act
            updated_user = user_service.update_user(mock_db, user_in_db, full_name=updated_full_name, password=updated_password)

        # Assert
        assert updated_user.full_name == updated_full_name
        assert updated_user.hashed_password == "new_hashed_password"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_delete_user_success(self):
        # Arrange
        mock_db = MagicMock(spec=Session)
        user_in_db = User(email="test@example.com", full_name="Test User", hashed_password="hashed_secret")
        mock_db.query().filter().first.return_value = user_in_db

        # Act
        result = user_service.delete_user(mock_db, user_in_db)

        # Assert
        assert result is True
        mock_db.delete.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_delete_user_failure(self):
        # Arrange
        mock_db = MagicMock(spec=Session)
        user_in_db = User(email="test@example.com", full_name="Test User", hashed_password="hashed_secret")
        mock_db.query().filter().first.return_value = user_in_db
        mock_db.delete.side_effect = Exception("DB error")

        # Act
        result = user_service.delete_user(mock_db, user_in_db)

        # Assert
        assert result is False
        mock_db.rollback.assert_called_once()

    def test_authenticate_user_success(self):
        # Arrange
        mock_db = MagicMock(spec=Session)
        user_in_db = User(email="test@example.com", hashed_password="hashed_secret")
        mock_db.query().filter().first.return_value = user_in_db

        with patch("app.services.user_service.verify_password", return_value=True):
            # Act
            user = user_service.authenticate_user(mock_db, "test@example.com", "password")

        # Assert
        assert user.email == "test@example.com"
        mock_db.query().filter().first.assert_called_once()

    def test_authenticate_user_invalid_credentials_raises(self):
        # Arrange
        mock_db = MagicMock(spec=Session)
        user_in_db = User(email="test@example.com", hashed_password="hashed_secret")
        mock_db.query().filter().first.return_value = user_in_db

        with patch("app.services.user_service.verify_password", return_value=False):
            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                user_service.authenticate_user(mock_db, "test@example.com", "wrongpassword")
            assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc.value.detail == "Invalid credentials"


    def test_get_user_from_token_success(self):
        # Arrange
        mock_db = MagicMock(spec=Session)
        user_in_db = User(email="test@example.com", hashed_password="hashed_secret")
        mock_db.query().filter().first.return_value = user_in_db
        token = "valid_token"
        payload = {"sub": "test@example.com"}

        with patch("app.services.user_service.verify_token", return_value=payload):
            # Act
            user = user_service.get_user_from_token(mock_db, token)

        # Assert
        assert user.email == "test@example.com"
        mock_db.query().filter().first.assert_called_once()

    def test_get_user_from_token_invalid_raises(self):
        # Arrange
        mock_db = MagicMock(spec=Session)
        token = "invalid_token"
        with patch("app.services.user_service.verify_token", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                user_service.get_user_from_token(mock_db, token)
            assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc.value.detail == "Invalid authentication credentials"

    def test_list_all_users_success(self):
        # Arrange
        mock_db = MagicMock(spec=Session)
        users_in_db = [User(email="user1@example.com"), User(email="user2@example.com")]
        mock_db.query().all.return_value = users_in_db

        # Act
        users = user_service.list_all_users(mock_db)

        # Assert
        assert len(users) == 2
        assert users[0].email == "user1@example.com"
        assert users[1].email == "user2@example.com"
        mock_db.query().all.assert_called_once()

