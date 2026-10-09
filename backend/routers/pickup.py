"""
Pickup router for e-waste pickup scheduling and management.
Handles pickup creation, listing, cancellation, and completion with EcoPoints rewards.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field, validator
import random
import uuid as uuid_lib

from database import get_db
from models import Pickup, User, Classification, EcoPointTransaction, PickupStatus
from dependencies import get_current_active_user


router = APIRouter(
    prefix="/api/pickups",
    tags=["Pickups"],
)


# Pydantic schemas
class PickupAddress(BaseModel):
    """Address information for pickup location."""
    street: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    pincode: str = Field(..., min_length=1, max_length=20)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class CreatePickupRequest(BaseModel):
    """Request body for creating a new pickup."""
    classification_id: Optional[str] = Field(None, description="Optional classification ID to link")
    item_description: str = Field(..., min_length=1, max_length=500, description="Description of item(s) for pickup")
    estimated_weight_kg: Optional[float] = Field(None, ge=0, le=1000)
    scheduled_at: datetime = Field(..., description="Preferred pickup date and time")
    address: PickupAddress
    notes: Optional[str] = Field(None, max_length=1000)

    @validator('scheduled_at')
    def validate_scheduled_at(cls, v):
        """Ensure scheduled_at is in the future."""
        now = datetime.now(timezone.utc)
        if v <= now:
            raise ValueError('Pickup date must be in the future')
        # Don't allow pickups more than 30 days in advance
        if v > now + timedelta(days=30):
            raise ValueError('Pickup date cannot be more than 30 days in advance')
        return v


class PickupResponse(BaseModel):
    """Response for a single pickup."""
    pickup_id: str
    user_id: str
    collector_id: Optional[str]
    classification_id: Optional[str]
    item_description: str
    scheduled_at: str
    address: dict
    status: str
    otp: Optional[str]  # Only shown to the user who created the pickup
    otp_expires_at: Optional[str]
    cancellation_reason: Optional[str]
    eco_points_awarded: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class CancelPickupRequest(BaseModel):
    """Request body for cancelling a pickup."""
    reason: str = Field(..., min_length=1, max_length=500)


class CompletePickupRequest(BaseModel):
    """Request body for completing a pickup (collector only)."""
    otp: str = Field(..., min_length=6, max_length=6)


def generate_otp() -> str:
    """Generate a 6-digit OTP."""
    return f"{random.randint(100000, 999999)}"


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Schedule a new pickup",
    description="Create a new e-waste pickup request. Generates OTP valid for 30 minutes.",
)
async def create_pickup(
    request: CreatePickupRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Schedule a new e-waste pickup.

    Creates a pickup request with status 'pending' and generates a 6-digit OTP
    valid for 30 minutes. The OTP will be used for verification at handoff.

    Optionally links to a classification if classification_id is provided.
    """
    # Validate classification_id if provided
    classification = None
    if request.classification_id:
        try:
            classification_uuid = uuid_lib.UUID(request.classification_id)
            result = await db.execute(
                select(Classification).where(
                    and_(
                        Classification.classification_id == classification_uuid,
                        Classification.user_id == current_user.user_id
                    )
                )
            )
            classification = result.scalar_one_or_none()

            if not classification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Classification not found or does not belong to you"
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid classification_id format"
            )

    # Generate OTP
    otp = generate_otp()
    otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

    # Create pickup
    new_pickup = Pickup(
        user_id=current_user.user_id,
        classification_id=classification.classification_id if classification else None,
        item_description=request.item_description,
        scheduled_at=request.scheduled_at,
        address_street=request.address.street,
        address_city=request.address.city,
        address_state=request.address.state,
        address_pincode=request.address.pincode,
        address_lat=Decimal(str(request.address.lat)),
        address_lng=Decimal(str(request.address.lng)),
        otp=otp,
        otp_expires_at=otp_expires_at,
        status=PickupStatus.PENDING,
    )

    try:
        db.add(new_pickup)
        await db.commit()
        await db.refresh(new_pickup)

        return {
            "pickup_id": str(new_pickup.pickup_id),
            "status": new_pickup.status.value,
            "scheduled_at": new_pickup.scheduled_at.isoformat(),
            "otp": new_pickup.otp,
            "otp_expires_at": new_pickup.otp_expires_at.isoformat(),
            "message": "Pickup scheduled successfully. Keep your OTP safe for verification.",
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pickup: {str(e)}"
        )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Get user's pickups",
    description="Retrieve all pickups for the authenticated user.",
)
async def get_user_pickups(
    status_filter: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all pickups for the authenticated user.

    Optionally filter by status (pending, accepted, in_transit, completed, cancelled).
    Returns pickups in reverse chronological order (newest first).
    """
    query = select(Pickup).where(Pickup.user_id == current_user.user_id)

    # Apply status filter if provided
    if status_filter:
        try:
            status_enum = PickupStatus(status_filter.lower())
            query = query.where(Pickup.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join([s.value for s in PickupStatus])}"
            )

    query = query.order_by(desc(Pickup.created_at)).limit(limit)

    result = await db.execute(query)
    pickups = result.scalars().all()

    # Check which pickups have eco points awarded
    pickup_ids = [p.pickup_id for p in pickups]
    transactions_result = await db.execute(
        select(EcoPointTransaction.pickup_id).where(
            EcoPointTransaction.pickup_id.in_(pickup_ids)
        )
    )
    awarded_pickup_ids = {row[0] for row in transactions_result.fetchall()}

    return {
        "pickups": [
            {
                "pickup_id": str(p.pickup_id),
                "classification_id": str(p.classification_id) if p.classification_id else None,
                "item_description": p.item_description,
                "scheduled_at": p.scheduled_at.isoformat(),
                "address": {
                    "street": p.address_street,
                    "city": p.address_city,
                    "state": p.address_state,
                    "pincode": p.address_pincode,
                    "lat": float(p.address_lat),
                    "lng": float(p.address_lng),
                },
                "status": p.status.value,
                "otp": p.otp if p.status in [PickupStatus.PENDING, PickupStatus.ACCEPTED] else None,
                "otp_expires_at": p.otp_expires_at.isoformat() if p.otp_expires_at else None,
                "cancellation_reason": p.cancellation_reason,
                "eco_points_awarded": p.pickup_id in awarded_pickup_ids,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat(),
            }
            for p in pickups
        ],
        "total": len(pickups),
    }


@router.get(
    "/{pickup_id}",
    status_code=status.HTTP_200_OK,
    summary="Get pickup details",
    description="Get detailed information about a specific pickup.",
)
async def get_pickup(
    pickup_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific pickup.

    Only the user who created the pickup can view its details.
    """
    try:
        pickup_uuid = uuid_lib.UUID(pickup_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pickup_id format"
        )

    result = await db.execute(
        select(Pickup).where(Pickup.pickup_id == pickup_uuid)
    )
    pickup = result.scalar_one_or_none()

    if not pickup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pickup not found"
        )

    # Verify ownership
    if pickup.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this pickup"
        )

    # Check if eco points awarded
    transaction_result = await db.execute(
        select(EcoPointTransaction).where(
            EcoPointTransaction.pickup_id == pickup.pickup_id
        )
    )
    transaction = transaction_result.scalar_one_or_none()

    return {
        "pickup_id": str(pickup.pickup_id),
        "classification_id": str(pickup.classification_id) if pickup.classification_id else None,
        "item_description": pickup.item_description,
        "scheduled_at": pickup.scheduled_at.isoformat(),
        "address": {
            "street": pickup.address_street,
            "city": pickup.address_city,
            "state": pickup.address_state,
            "pincode": pickup.address_pincode,
            "lat": float(pickup.address_lat),
            "lng": float(pickup.address_lng),
        },
        "status": pickup.status.value,
        "otp": pickup.otp if pickup.status in [PickupStatus.PENDING, PickupStatus.ACCEPTED] else None,
        "otp_expires_at": pickup.otp_expires_at.isoformat() if pickup.otp_expires_at else None,
        "cancellation_reason": pickup.cancellation_reason,
        "eco_points_awarded": transaction is not None,
        "eco_points_amount": transaction.points if transaction else None,
        "created_at": pickup.created_at.isoformat(),
        "updated_at": pickup.updated_at.isoformat(),
    }


@router.post(
    "/{pickup_id}/cancel",
    status_code=status.HTTP_200_OK,
    summary="Cancel a pickup",
    description="Cancel a pickup request. Only allowed for pending or accepted status.",
)
async def cancel_pickup(
    pickup_id: str,
    request: CancelPickupRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel a pickup request.

    Only allowed when status is 'pending' or 'accepted'.
    Cannot cancel if already in_transit or completed.
    """
    try:
        pickup_uuid = uuid_lib.UUID(pickup_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pickup_id format"
        )

    result = await db.execute(
        select(Pickup).where(Pickup.pickup_id == pickup_uuid)
    )
    pickup = result.scalar_one_or_none()

    if not pickup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pickup not found"
        )

    # Verify ownership
    if pickup.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to cancel this pickup"
        )

    # Check if cancellation is allowed
    if pickup.status not in [PickupStatus.PENDING, PickupStatus.ACCEPTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel pickup with status '{pickup.status.value}'. Only pending or accepted pickups can be cancelled."
        )

    try:
        pickup.status = PickupStatus.CANCELLED
        pickup.cancellation_reason = request.reason
        await db.commit()
        await db.refresh(pickup)

        return {
            "pickup_id": str(pickup.pickup_id),
            "status": pickup.status.value,
            "cancellation_reason": pickup.cancellation_reason,
            "message": "Pickup cancelled successfully"
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel pickup: {str(e)}"
        )


@router.post(
    "/{pickup_id}/complete",
    status_code=status.HTTP_200_OK,
    summary="Complete a pickup and award EcoPoints",
    description="Mark pickup as completed with OTP verification. Awards 75 EcoPoints on success.",
)
async def complete_pickup(
    pickup_id: str,
    request: CompletePickupRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Complete a pickup and award EcoPoints.

    Verifies OTP, marks pickup as completed, and awards 75 EcoPoints to the user.
    Prevents duplicate rewards by checking for existing transactions.

    In a real system, this would be called by the collector after verifying identity.
    For demo purposes, users can complete their own pickups with OTP.
    """
    try:
        pickup_uuid = uuid_lib.UUID(pickup_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pickup_id format"
        )

    result = await db.execute(
        select(Pickup).where(Pickup.pickup_id == pickup_uuid)
    )
    pickup = result.scalar_one_or_none()

    if not pickup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pickup not found"
        )

    # Verify ownership (in production, collector would verify)
    if pickup.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to complete this pickup"
        )

    # Check if already completed
    if pickup.status == PickupStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pickup is already completed"
        )

    # Verify OTP
    if not pickup.is_otp_valid(request.otp):
        if datetime.now(timezone.utc) > pickup.otp_expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )

    # Check if EcoPoints already awarded (prevent duplicates)
    existing_transaction = await db.execute(
        select(EcoPointTransaction).where(
            EcoPointTransaction.pickup_id == pickup.pickup_id
        )
    )
    if existing_transaction.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="EcoPoints already awarded for this pickup"
        )

    try:
        # Mark pickup as completed
        pickup.status = PickupStatus.COMPLETED

        # Award EcoPoints (75 points per completed pickup as per PRD)
        ECOPOINTS_PER_PICKUP = 75

        # Update user's eco_points balance
        current_user.eco_points += ECOPOINTS_PER_PICKUP

        # Create transaction record
        transaction = EcoPointTransaction(
            user_id=current_user.user_id,
            pickup_id=pickup.pickup_id,
            points=ECOPOINTS_PER_PICKUP,
            reason=f"Completed pickup: {pickup.item_description[:50]}"
        )

        db.add(transaction)
        await db.commit()
        await db.refresh(pickup)
        await db.refresh(current_user)
        await db.refresh(transaction)

        return {
            "pickup_id": str(pickup.pickup_id),
            "status": pickup.status.value,
            "eco_points_awarded": ECOPOINTS_PER_PICKUP,
            "new_balance": current_user.eco_points,
            "transaction_id": str(transaction.transaction_id),
            "message": f"Pickup completed! You earned {ECOPOINTS_PER_PICKUP} EcoPoints."
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete pickup: {str(e)}"
        )


@router.get(
    "/stats/summary",
    status_code=status.HTTP_200_OK,
    summary="Get user's pickup statistics",
    description="Get summary statistics for the authenticated user's pickups.",
)
async def get_pickup_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get summary statistics for user's pickups.

    Returns counts by status and total eco points earned.
    """
    result = await db.execute(
        select(Pickup).where(Pickup.user_id == current_user.user_id)
    )
    pickups = result.scalars().all()

    stats = {
        "total_pickups": len(pickups),
        "pending": sum(1 for p in pickups if p.status == PickupStatus.PENDING),
        "accepted": sum(1 for p in pickups if p.status == PickupStatus.ACCEPTED),
        "in_transit": sum(1 for p in pickups if p.status == PickupStatus.IN_TRANSIT),
        "completed": sum(1 for p in pickups if p.status == PickupStatus.COMPLETED),
        "cancelled": sum(1 for p in pickups if p.status == PickupStatus.CANCELLED),
        "eco_points_balance": current_user.eco_points,
    }

    return stats
