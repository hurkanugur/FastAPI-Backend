import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.services import auth_service
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, Token

@pytest.mark.unit
class TestAuthService:

    def test_register_user_success(self):
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_db.query().filter().first.return_value = None  # No existing user
        user_create = UserCreate(email="test@example.com", password="secret", full_name="Test User")
        hashed_password = "hashed_secret"

        with patch("app.services.auth_service.get_password_hash", return_value=hashed_password):
            # Act
            new_user = auth_service.register_user(mock_db, user_create)

        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(new_user)
        assert new_user.email == user_create.email
        assert new_user.full_name == user_create.full_name
        assert new_user.hashed_password == hashed_password

    def test_register_user_existing_email_raises(self):
        # Arrange
        mock_db = MagicMock(spec=Session)
        existing_user = User(email="test@example.com")
        mock_db.query().filter().first.return_value = existing_user
        user_create = UserCreate(email="test@example.com", password="secret", full_name="Test User")

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            auth_service.register_user(mock_db, user_create)
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.value.detail == "Email already registered"

    def test_login_user_success(self):
        # Arrange
        mock_db = MagicMock(spec=Session)
        user_in_db = User(email="test@example.com", hashed_password="hashed_secret")
        mock_db.query().filter().first.return_value = user_in_db
        user_create = UserCreate(email="test@example.com", password="secret")
        access_token = "access123"
        refresh_token = "refresh123"

        with patch("app.services.auth_service.verify_password", return_value=True), \
             patch("app.services.auth_service.create_access_token", return_value=access_token), \
             patch("app.services.auth_service.create_refresh_token", return_value=refresh_token):
            # Act
            token = auth_service.login_user(mock_db, user_create)

        # Assert
        assert isinstance(token, Token)
        assert token.access_token == access_token
        assert token.refresh_token == refresh_token
        assert token.token_type == "bearer"

    def test_login_user_invalid_credentials_raises(self):
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_db.query().filter().first.return_value = None  # User not found
        user_create = UserCreate(email="test@example.com", password="secret")

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            auth_service.login_user(mock_db, user_create)
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == "Invalid credentials"

    def test_refresh_tokens_success(self):
        # Arrange
        refresh_token_value = "refresh123"
        payload = {"sub": "test@example.com"}
        new_access_token = "new_access"
        new_refresh_token = "new_refresh"

        with patch("app.services.auth_service.verify_token", return_value=payload), \
             patch("app.services.auth_service.create_access_token", return_value=new_access_token), \
             patch("app.services.auth_service.create_refresh_token", return_value=new_refresh_token):
            # Act
            token = auth_service.refresh_tokens(refresh_token_value)

        # Assert
        assert isinstance(token, Token)
        assert token.access_token == new_access_token
        assert token.refresh_token == new_refresh_token
        assert token.token_type == "bearer"

    def test_refresh_tokens_invalid_raises(self):
        # Arrange
        refresh_token_value = "invalid_refresh"

        with patch("app.services.auth_service.verify_token", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                auth_service.refresh_tokens(refresh_token_value)
            assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc.value.detail == "Invalid refresh token"
