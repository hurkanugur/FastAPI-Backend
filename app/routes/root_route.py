from fastapi import APIRouter
from app.core.config import app_settings
from typing import Dict

router = APIRouter()


@router.get(
    "/",
    summary="Root endpoint",
    response_description="Welcome message with application name",
)
def read_root() -> Dict[str, str]:
    """
    Root endpoint of the API.

    Returns:
        dict: A welcome message containing the application name from the settings.
    """
    return {"message": f"Welcome to {app_settings.app_name}!"}
