from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_admin_user, get_current_user
from app.core.database import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserInfo, UserCreate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "/me",
    response_model=UserInfo,
    summary="Get current user profile",
    description="Get profile info of the authenticated user."
)
def read_current_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> UserInfo:
    """Return profile of the authenticated user."""
    return user_service.get_user_by_email(email=current_user.email, db=db)

@router.get(
    "/",
    response_model=List[UserInfo],
    summary="List all users (admin)",
    description="Retrieve all users. Admins only."
)
def list_users(db: Session = Depends(get_db), admin_user: User = Depends(get_admin_user)) -> List[UserInfo]:
    """List all users (admin only)."""
    return user_service.list_all_users(db=db)

@router.put(
    "/me",
    response_model=UserInfo,
    summary="Update current user profile",
    description="Update full name or password of the authenticated user."
)
def update_current_user(updated_data: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> User:
    """Update the authenticated user's profile."""
    return user_service.update_user(db=db, current_user=current_user, full_name=updated_data.full_name, password=updated_data.password)

@router.delete(
    "/me",
    response_model=dict,
    summary="Delete current user profile",
    description="Delete the authenticated user's account."
)
def delete_current_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    """Delete the authenticated user's account."""
    user_service.delete_user(db=db, user=current_user)
    return {"detail": "User account deleted successfully."}
