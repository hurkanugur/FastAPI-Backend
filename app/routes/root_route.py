from fastapi import APIRouter
from app.core.config import app_settings
from typing import Dict

router = APIRouter()

@router.get(
    "/", 
    summary="Root endpoint",
    description="This is the root endpoint of the API. It returns a welcome message with the application's name."
)
def read_root() -> Dict[str, str]:
    """Return a welcome message with the application name."""
    return {"message": f"Welcome to {app_settings.app_name}!"}
