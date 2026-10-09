"""
Authentication router for user registration, login, and verification.
Handles all auth-related endpoints under /api/auth.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

from database import get_db
from models import User, UserRole
from schemas import (
    UserRegisterRequest, UserRegisterResponse, UserResponse, ErrorResponse,
    UserLoginRequest, TokenResponse
)
from security import hash_password, verify_password, create_access_token
from dependencies import get_current_active_user
from config import settings


# Create router with prefix and tags
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        409: {"model": ErrorResponse, "description": "Conflict - duplicate email or phone"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, password, and optional phone number. "
                "Passwords are securely hashed using Argon2. Email and phone must be unique.",
    responses={
        201: {
            "description": "User successfully registered",
            "model": UserRegisterResponse,
        },
        400: {
            "description": "Invalid input data",
            "content": {
                "application/json": {
                    "example": {"detail": "Password must contain at least one digit"}
                }
            },
        },
        409: {
            "description": "Email or phone already registered",
            "content": {
                "application/json": {
                    "examples": {
                        "email_exists": {"value": {"detail": "Email already registered"}},
                        "phone_exists": {"value": {"detail": "Phone number already registered"}},
                    }
                }
            },
        },
    },
)
async def register_user(
    user_data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserRegisterResponse:
    """
    Register a new user account.

    This endpoint:
    1. Validates input data (email format, password strength, etc.)
    2. Checks for duplicate email and phone number
    3. Hashes the password securely using bcrypt
    4. Creates user with default role 'user' and 0 eco_points
    5. Returns user data (without password_hash)

    Args:
        user_data: User registration data (name, email, phone, password)
        db: Database session (injected)

    Returns:
        UserRegisterResponse with success message and user data

    Raises:
        HTTPException 409: If email or phone already exists
        HTTPException 400: If validation fails
        HTTPException 500: If database operation fails
    """

    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Check if phone already exists (only if phone is provided)
    if user_data.phone:
        result = await db.execute(
            select(User).where(User.phone == user_data.phone)
        )
        existing_phone = result.scalar_one_or_none()

        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number already registered"
            )

    # Hash the password securely
    password_hash = hash_password(user_data.password)

    # Create new user with default values
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=password_hash,
        role=UserRole.USER,  # Default role
        eco_points=0,  # Starting points
    )

    try:
        # Add user to database
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Convert SQLAlchemy model to response schema
        # This automatically excludes password_hash
        user_response = UserResponse(
            user_id=str(new_user.user_id),
            name=new_user.name,
            email=new_user.email,
            phone=new_user.phone,
            role=new_user.role.value,  # Convert enum to string
            eco_points=new_user.eco_points,
            created_at=new_user.created_at,
        )

        return UserRegisterResponse(
            message="User registered successfully",
            user=user_response
        )

    except IntegrityError as e:
        # Catch any database constraint violations
        await db.rollback()

        # Provide specific error message based on constraint
        error_msg = str(e.orig).lower()
        if 'email' in error_msg:
            detail = "Email already registered"
        elif 'phone' in error_msg:
            detail = "Phone number already registered"
        else:
            detail = "User registration failed due to data conflict"

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )

    except Exception as e:
        # Catch any other unexpected errors
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}"
        )



@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with email and password",
    description="Authenticate a user and return a JWT access token. "
                "The token expires after the configured time period and must be included "
                "in the Authorization header as 'Bearer <token>' for protected endpoints.",
    responses={
        200: {
            "description": "Login successful",
            "model": TokenResponse,
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid email or password"}
                }
            },
        },
    },
)
async def login(
    login_data: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate a user and return a JWT access token.

    This endpoint:
    1. Validates the email and password
    2. Verifies the password using Argon2
    3. Creates a signed JWT access token
    4. Returns the token and user profile

    Security:
    - Passwords are never stored or returned in plaintext
    - Uses constant-time comparison to prevent timing attacks
    - Returns generic error message without revealing which field was incorrect

    Args:
        login_data: User login credentials (email and password)
        db: Database session (injected)

    Returns:
        TokenResponse with JWT access token and user profile

    Raises:
        HTTPException 401: If email doesn't exist or password is incorrect
    """

    # Fetch user by email
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )
    user = result.scalar_one_or_none()

    # Security: Don't reveal whether email exists or password is wrong
    # Always use generic error message
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password using Argon2
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is soft-deleted
    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id)},
        expires_delta=access_token_expires
    )

    # Prepare user response (excludes password_hash)
    user_response = UserResponse(
        user_id=str(user.user_id),
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=user.role.value,
        eco_points=user.eco_points,
        created_at=user.created_at,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
    description="Retrieve the profile of the currently authenticated user. "
                "Requires a valid JWT access token in the Authorization header.",
    responses={
        200: {
            "description": "User profile retrieved successfully",
            "model": UserResponse,
        },
        401: {
            "description": "Invalid or expired token",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            },
        },
    },
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """
    Get the currently authenticated user's profile.

    This endpoint:
    1. Validates the JWT token from Authorization header
    2. Retrieves the user from the database
    3. Returns the user profile (without password_hash)

    Authentication:
    - Requires valid JWT token in Authorization header: "Bearer <token>"
    - Token must not be expired
    - User must exist and be active (not soft-deleted)

    Args:
        current_user: Authenticated user (injected by dependency)

    Returns:
        UserResponse with current user's profile data
    """
    return UserResponse(
        user_id=str(current_user.user_id),
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        role=current_user.role.value,
        eco_points=current_user.eco_points,
        created_at=current_user.created_at,
    )
