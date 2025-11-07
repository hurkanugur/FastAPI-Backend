from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_admin_user
from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserInfo, UserCreate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


# ===============================
# Get current user profile
# ===============================
@router.get(
    "/me",
    response_model=UserInfo,
    summary="Get current user profile",
    description="Retrieve the profile information of the currently authenticated user. "
                "Requires a valid Bearer token in the Authorization header."
)
def read_current_user(
    current_user: User = Depends(get_current_user)
):
    """
    Returns the profile of the currently authenticated user.

    Args:
        current_user (User): User object obtained via token dependency

    Returns:
        UserInfo: User details including id, email, full name, and creation timestamp
    """
    return user_service.get_user_by_email(email=current_user.email, db=current_user.__dict__.get("db", None) or None)


# ===============================
# List all users (admin only)
# ===============================
@router.get(
    "/",
    response_model=List[UserInfo],
    summary="List all users (admin)",
    description="Retrieve a list of all registered users. "
                "Intended for admin access only."
)
def list_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
) -> List[UserInfo]:
    """
    List all registered users in the system. Only accessible to admins.

    Args:
        db (Session): SQLAlchemy database session
        admin_user (User): Currently authenticated admin user

    Returns:
        List[UserInfo]: List of all users
    """
    return user_service.list_all_users(db=db)


# ===============================
# Update current user
# ===============================
@router.put(
    "/me",
    response_model=UserInfo,
    summary="Update current user profile",
    description="Update the currently authenticated user's profile information, including full name and password."
)
def update_current_user(
    updated_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Update the profile of the currently authenticated user.

    Args:
        updated_data (UserCreate): New data for the user (full_name, password)
        db (Session): SQLAlchemy database session (injected via Depends)
        current_user (User): Currently authenticated user

    Returns:
        UserInfo: Updated user details
    """
    return user_service.update_user_profile(
        db=db,
        user=current_user,
        full_name=updated_data.full_name,
        password=updated_data.password
    )
