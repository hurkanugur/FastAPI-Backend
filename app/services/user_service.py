from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user_model import User
from app.core.security import verify_token, get_password_hash, verify_password

def get_user_by_email(db: Session, email: str) -> User:
    """Retrieve a user by their email address."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def update_user(db: Session, current_user: User, full_name: str = None, password: str = None) -> User:
    """Update user's profile fields such as full name and password."""
    if full_name:
        current_user.full_name = full_name
    if password:
        current_user.hashed_password = get_password_hash(password)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

def delete_user(db: Session, user: User) -> bool:
    """Delete a user from the database."""
    try:
        db.delete(user)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Authenticate a user using email and password."""
    user = get_user_by_email(db, email)
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return user


def get_user_from_token(db: Session, token: str) -> User:
    """Retrieve the currently authenticated user from a JWT token."""
    payload = verify_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    return get_user_by_email(db, payload["sub"])


def list_all_users(db: Session) -> list[User]:
    """Retrieve a list of all registered users."""
    return db.query(User).all()
