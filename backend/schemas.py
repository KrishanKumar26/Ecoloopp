"""
Pydantic schemas for request/response validation.
Separates API contracts from database models.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


# ============================================================================
# Authentication Schemas
# ============================================================================

class UserRegisterRequest(BaseModel):
    """Request schema for user registration."""
    name: str = Field(..., min_length=1, max_length=255, description="Full name of the user")
    email: EmailStr = Field(..., description="Valid email address")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number (optional)")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 characters)")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty or just whitespace")
        return v.strip()

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format if provided."""
        if v is None:
            return v

        # Remove whitespace
        v = v.strip()
        if not v:
            return None

        # Basic phone validation: allow +, digits, spaces, hyphens, parentheses
        if not re.match(r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$', v):
            raise ValueError("Invalid phone number format")

        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Check for at least one digit
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one digit")

        # Check for at least one letter
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError("Password must contain at least one letter")

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone": "+919876543210",
                    "password": "SecurePass123"
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """Response schema for user data (never includes password_hash)."""
    user_id: str
    name: str
    email: str
    phone: Optional[str]
    role: str
    eco_points: int
    created_at: datetime

    model_config = {
        "from_attributes": True,  # Enable ORM mode for SQLAlchemy models
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone": "+919876543210",
                    "role": "user",
                    "eco_points": 0,
                    "created_at": "2026-10-08T15:30:00Z"
                }
            ]
        }
    }


class UserRegisterResponse(BaseModel):
    """Response schema for successful registration."""
    message: str
    user: UserResponse

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "User registered successfully",
                    "user": {
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "phone": "+919876543210",
                        "role": "user",
                        "eco_points": 0,
                        "created_at": "2026-10-08T15:30:00Z"
                    }
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    detail: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": "Email already registered"
                }
            ]
        }
    }


class UserLoginRequest(BaseModel):
    """Request schema for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "john.doe@example.com",
                    "password": "SecurePass123"
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    """Response schema for successful authentication."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    user: UserResponse = Field(..., description="Authenticated user's profile")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "user": {
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "phone": "+919876543210",
                        "role": "user",
                        "eco_points": 0,
                        "created_at": "2026-10-08T15:30:00Z"
                    }
                }
            ]
        }
    }
