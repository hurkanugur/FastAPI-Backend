import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.services import user_service
from app.models.user_model import User
from app.core.security import create_access_token, get_password_hash

def test_get_user_by_email(db_session: Session):
    user = User(email="user1@example.com", hashed_password=get_password_hash("pass"), full_name="User One")
    db_session.add(user)
    db_session.commit()

    retrieved = user_service.get_user_by_email(db_session, "user1@example.com")
    assert retrieved.email == "user1@example.com"

    with pytest.raises(HTTPException):
        user_service.get_user_by_email(db_session, "nonexistent@example.com")


def test_update_user_profile(db_session: Session):
    user = User(email="update@example.com", hashed_password=get_password_hash("oldpass"), full_name="Old Name")
    db_session.add(user)
    db_session.commit()

    updated = user_service.update_user_profile(db_session, user, full_name="New Name", password="newpass")
    assert updated.full_name == "New Name"
    assert updated.hashed_password != "newpass"  # hashed


def test_authenticate_user_success(db_session: Session):
    user = User(email="auth@example.com", hashed_password=get_password_hash("secret"), full_name="Auth User")
    db_session.add(user)
    db_session.commit()

    authenticated = user_service.authenticate_user(db_session, "auth@example.com", "secret")
    assert authenticated.email == "auth@example.com"

def test_authenticate_user_invalid(db_session: Session):
    user = User(email="fail@example.com", hashed_password=get_password_hash("secret"), full_name="Fail User")
    db_session.add(user)
    db_session.commit()

    with pytest.raises(HTTPException):
        user_service.authenticate_user(db_session, "fail@example.com", "wrongpassword")


def test_get_user_from_token(db_session: Session, monkeypatch):
    user = User(email="token@example.com", hashed_password=get_password_hash("secret"), full_name="Token User")
    db_session.add(user)
    db_session.commit()

    token_str = create_access_token({"sub": "token@example.com"})

    monkeypatch.setattr("app.core.security.verify_token", lambda t: {"sub": "token@example.com"})
    retrieved = user_service.get_user_from_token(db_session, token_str)
    assert retrieved.email == "token@example.com"

def test_get_user_from_token_invalid(db_session: Session, monkeypatch):
    monkeypatch.setattr("app.core.security.verify_token", lambda t: None)
    with pytest.raises(HTTPException):
        user_service.get_user_from_token(db_session, "invalidtoken")


def test_list_all_users(db_session: Session):
    user1 = User(email="list1@example.com", hashed_password=get_password_hash("pass1"), full_name="List One")
    user2 = User(email="list2@example.com", hashed_password=get_password_hash("pass2"), full_name="List Two")
    db_session.add_all([user1, user2])
    db_session.commit()

    all_users = user_service.list_all_users(db_session)
    emails = [u.email for u in all_users]
    assert "list1@example.com" in emails
    assert "list2@example.com" in emails
