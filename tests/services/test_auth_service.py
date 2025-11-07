import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.services import auth_service
from app.schemas.user_schema import UserCreate
from app.models.user_model import User
from app.core.security import create_refresh_token

def test_register_user(db_session: Session):
    user_create = UserCreate(email="test1@example.com", password="password123", full_name="Test One")
    
    user = auth_service.register_user(db_session, user_create)
    
    assert isinstance(user, User)
    assert user.email == "test1@example.com"
    assert user.full_name == "Test One"
    assert user.hashed_password != "password123"  # hashed

def test_register_user_duplicate_email(db_session: Session):
    user_create = UserCreate(email="duplicate@example.com", password="pass", full_name="Duplicate")
    auth_service.register_user(db_session, user_create)
    
    with pytest.raises(HTTPException) as exc_info:
        auth_service.register_user(db_session, user_create)
    
    assert exc_info.value.status_code == 400
    assert "Email already registered" in exc_info.value.detail

def test_login_user_success(db_session: Session):
    # First register
    user_create = UserCreate(email="login@example.com", password="mypassword", full_name="Login User")
    auth_service.register_user(db_session, user_create)
    
    token_obj = auth_service.login_user(db_session, UserCreate(email="login@example.com", password="mypassword", full_name=""))
    
    assert token_obj.access_token is not None
    assert token_obj.refresh_token is not None
    assert token_obj.token_type == "bearer"

def test_login_user_invalid_password(db_session: Session):
    user_create = UserCreate(email="wrongpass@example.com", password="correct", full_name="Wrong Pass")
    auth_service.register_user(db_session, user_create)
    
    with pytest.raises(HTTPException) as exc_info:
        auth_service.login_user(db_session, UserCreate(email="wrongpass@example.com", password="wrong", full_name=""))
    
    assert exc_info.value.status_code == 401
    assert "Invalid credentials" in exc_info.value.detail

def test_refresh_tokens_success():
    # create a refresh token for test
    token_str = create_refresh_token({"sub": "user@example.com"})
    # mock verify_token to just return payload for test
    from app.core.security import verify_token as original_verify
    import app.core.security
    app.core.security.verify_token = lambda token: {"sub": "user@example.com"}
    
    token_obj = auth_service.refresh_tokens(token_str)
    assert token_obj.access_token is not None
    assert token_obj.refresh_token is not None
    assert token_obj.token_type == "bearer"
    
    # restore original verify_token
    app.core.security.verify_token = original_verify

def test_refresh_tokens_invalid():
    with pytest.raises(HTTPException) as exc_info:
        auth_service.refresh_tokens("invalidtoken")
    assert exc_info.value.status_code == 401
    assert "Invalid refresh token" in exc_info.value.detail
