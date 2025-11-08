from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# ===============================
# User request/response schemas
# ===============================

class UserCreate(BaseModel):
    """
    Schema for creating a new user (registration).
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    full_name: str | None = Field(None, description="User's full name")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123",
                "full_name": "John Doe"
            }
        }


class UserInfo(BaseModel):
    """
    Schema for returning user information (excluding password).
    """
    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User's email address")
    full_name: str | None = Field(None, description="User's full name")
    created_at: datetime = Field(..., description="Account creation timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "John Doe",
                "created_at": "2025-11-07T21:45:00Z"
            }
        }


# ===============================
# Token schemas
# ===============================

class Token(BaseModel):
    """
    Schema for JWT tokens returned by login or refresh endpoints.
    """
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type, usually 'bearer'")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR...",
                "token_type": "bearer"
            }
        }


class RefreshTokenRequest(BaseModel):
    """
    Schema for sending a refresh token to get a new access token.
    """
    refresh_token: str = Field(..., description="JWT refresh token")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR..."
            }
        }
