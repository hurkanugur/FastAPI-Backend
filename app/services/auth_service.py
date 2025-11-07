from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, Token
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)

def register_user(db: Session, user_create: UserCreate) -> User:
    """
    Register a new user in the database.

    Args:
        db (Session): SQLAlchemy database session
        user_create (UserCreate): User registration data (email, password, full_name)

    Returns:
        User: Newly created user object (without exposing password)
    """
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(user_create.password)
    new_user = User(
        email=user_create.email,
        hashed_password=hashed_password,
        full_name=user_create.full_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(db: Session, user_create: UserCreate) -> Token:
    """
    Authenticate a user and generate JWT access and refresh tokens.

    Args:
        db (Session): SQLAlchemy database session
        user_create (UserCreate): User login data (email, password)

    Returns:
        Token: Object containing access token, refresh token, and token type
    """
    user = db.query(User).filter(User.email == user_create.email).first()
    if not user or not verify_password(user_create.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


def refresh_tokens(refresh_token: str) -> Token:
    """
    Refresh JWT tokens using a valid refresh token.

    Args:
        refresh_token (str): Existing JWT refresh token

    Returns:
        Token: New access token, new refresh token, and token type
    """
    payload = verify_token(refresh_token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    new_access_token = create_access_token(data={"sub": payload["sub"]})
    new_refresh_token = create_refresh_token(data={"sub": payload["sub"]})
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )
