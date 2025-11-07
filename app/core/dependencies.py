from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user_model import User
from app.core.security import verify_token

# OAuth2 scheme to extract token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency to get the currently authenticated user.

    Args:
        db (Session): Database session (injected via Depends)
        token (str): JWT token extracted from the Authorization header

    Returns:
        User: The currently authenticated user object

    Raises:
        HTTPException 401: If the token is invalid or the user does not exist
    """
    payload = verify_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensure the current user has admin privileges.

    Raises:
        HTTPException: 403 Forbidden if user is not admin

    Returns:
        User: Admin user
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user