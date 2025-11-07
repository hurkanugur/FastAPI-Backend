from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.orm import Session
from typing import Annotated

from app.core.database import get_db
from app.schemas.user_schema import UserCreate, UserInfo, Token
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


# ===============================
# Register a new user
# ===============================
@router.post(
    "/register",
    response_model=UserInfo,
    summary="Register a new user",
    description="Create a new user account with email, password, and full name. "
                "The password is hashed before storing in the database.",
    status_code=status.HTTP_201_CREATED
)
def register(user_create: UserCreate, db: Annotated[Session, Depends(get_db)]) -> UserInfo:
    """
    Register a new user in the system.

    Args:
        user_create (UserCreate): User registration data
        db (Session): SQLAlchemy database session

    Returns:
        UserInfo: Newly created user (without password)
    """
    return auth_service.register_user(db=db, user_create=user_create)


# ===============================
# Login and get JWT token
# ===============================
@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticate a user using email and password. "
                "Returns an access token and refresh token if credentials are valid."
)
def login(user_create: UserCreate, db: Annotated[Session, Depends(get_db)]) -> Token:
    """
    Login a user and generate JWT tokens.

    Args:
        user_create (UserCreate): User login data
        db (Session): SQLAlchemy database session

    Returns:
        Token: Access token, refresh token, and token type
    """
    return auth_service.login_user(db=db, user_create=user_create)


# ===============================
# Refresh access token
# ===============================
@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Use a valid refresh token to generate a new access token. "
                "Returns both a new access token and refresh token."
)
def refresh_token(refresh_token: str = Body(..., description="Refresh token string")) -> Token:
    """
    Refresh JWT access token using a refresh token.

    Args:
        refresh_token (str): JWT refresh token

    Returns:
        Token: New access token, new refresh token, and token type
    """
    return auth_service.refresh_tokens(refresh_token=refresh_token)
