from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated
from app.core.database import get_db
from app.schemas.user_schema import RefreshTokenRequest, UserCreate, UserInfo, Token
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

# Register a new user
@router.post(
    "/register", 
    response_model=UserInfo, 
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, password, and full name. Password is hashed before storing."
)
def register(user_create: UserCreate, db: Annotated[Session, Depends(get_db)]) -> UserInfo:
    """Register a new user in the system."""
    return auth_service.register_user(db=db, user_create=user_create)

# User login and generate JWT tokens
@router.post(
    "/login", 
    response_model=Token,
    summary="Login a user and generate JWT tokens",
    description="Authenticate a user using email and password, and return access and refresh tokens."
)
def login(user_create: UserCreate, db: Annotated[Session, Depends(get_db)]) -> Token:
    """Login a user and generate JWT tokens."""
    return auth_service.login_user(db=db, user_create=user_create)

# Refresh JWT access token using a refresh token
@router.post(
    "/refresh", 
    response_model=Token,
    summary="Refresh JWT access token",
    description="Use a valid refresh token to generate a new access token and refresh token."
)
def refresh_token(refresh_token_request: RefreshTokenRequest) -> Token:
    """Refresh JWT access token using a refresh token."""
    return auth_service.refresh_tokens(refresh_token=refresh_token_request.refresh_token)
