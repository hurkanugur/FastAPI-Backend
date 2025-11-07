from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user_model import User
from app.core.security import verify_token, get_password_hash, verify_password

def get_user_by_email(db: Session, email: str) -> User:
    """
    Retrieve a user by their email address.

    Args:
        db (Session): SQLAlchemy database session
        email (str): Email of the user to retrieve

    Raises:
        HTTPException: 404 if user is not found

    Returns:
        User: User object corresponding to the given email
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def update_user_profile(db: Session, user: User, full_name: str = None, password: str = None) -> User:
    """
    Update user's profile fields such as full name and password.

    Args:
        db (Session): SQLAlchemy database session
        user (User): User object to update
        full_name (str, optional): New full name
        password (str, optional): New password

    Returns:
        User: Updated user object
    """
    if full_name:
        user.full_name = full_name
    if password:
        user.hashed_password = get_password_hash(password)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Authenticate a user using email and password.

    Args:
        db (Session): SQLAlchemy database session
        email (str): User's email
        password (str): User's password

    Raises:
        HTTPException: 401 if credentials are invalid

    Returns:
        User: Authenticated user object
    """
    user = get_user_by_email(db, email)
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return user


def get_user_from_token(db: Session, token: str) -> User:
    """
    Retrieve the currently authenticated user from a JWT token.

    Args:
        db (Session): SQLAlchemy database session
        token (str): JWT access token

    Raises:
        HTTPException: 401 if token is invalid or user not found

    Returns:
        User: User object corresponding to the JWT token
    """
    payload = verify_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    return get_user_by_email(db, payload["sub"])


def list_all_users(db: Session) -> list[User]:
    """
    Retrieve a list of all registered users.

    Args:
        db (Session): SQLAlchemy database session

    Returns:
        list[User]: List of all users in the database
    """
    return db.query(User).all()
