"""
Reusable dependencies for FastAPI endpoints.
Provides authentication and authorization utilities.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User
from security import decode_access_token


# HTTP Bearer token scheme for Swagger UI
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to get the currently authenticated user from JWT token.

    This dependency:
    1. Extracts the JWT token from the Authorization header
    2. Validates and decodes the token
    3. Retrieves the user from the database
    4. Returns the User object for use in endpoint handlers

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session (injected)

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException 401: If token is invalid, expired, or user not found

    Usage:
        @router.get("/protected")
        async def protected_route(
            current_user: User = Depends(get_current_user)
        ):
            return {"user_id": current_user.user_id}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Extract token from credentials
    token = credentials.credentials

    # Decode and validate token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Extract user_id from token payload
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Fetch user from database
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get the current active user (not soft-deleted).

    This is an extension of get_current_user that also checks
    if the user account has been soft-deleted.

    Args:
        current_user: User object from get_current_user dependency

    Returns:
        User: The authenticated active user

    Raises:
        HTTPException 401: If user account is deleted/inactive
    """
    if current_user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    return current_user
