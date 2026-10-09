"""
EcoPoints router for managing user rewards and transactions.
Handles point balance, transaction history, and leaderboard.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List

from database import get_db
from models import User, EcoPointTransaction
from dependencies import get_current_active_user


router = APIRouter(
    prefix="/api/ecopoints",
    tags=["EcoPoints"],
)


@router.get(
    "/balance",
    status_code=status.HTTP_200_OK,
    summary="Get user's EcoPoints balance",
    description="Get the current EcoPoints balance for the authenticated user.",
)
async def get_balance(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get the authenticated user's current EcoPoints balance.
    """
    return {
        "user_id": str(current_user.user_id),
        "balance": current_user.eco_points,
        "name": current_user.name,
    }


@router.get(
    "/transactions",
    status_code=status.HTTP_200_OK,
    summary="Get transaction history",
    description="Get the EcoPoints transaction history for the authenticated user.",
)
async def get_transactions(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get transaction history for the authenticated user.

    Returns all point awards and redemptions in reverse chronological order.
    """
    result = await db.execute(
        select(EcoPointTransaction)
        .where(EcoPointTransaction.user_id == current_user.user_id)
        .order_by(desc(EcoPointTransaction.created_at))
        .limit(limit)
    )
    transactions = result.scalars().all()

    return {
        "transactions": [
            {
                "transaction_id": str(t.transaction_id),
                "pickup_id": str(t.pickup_id) if t.pickup_id else None,
                "points": t.points,
                "reason": t.reason,
                "created_at": t.created_at.isoformat(),
            }
            for t in transactions
        ],
        "total": len(transactions),
        "current_balance": current_user.eco_points,
    }


@router.get(
    "/leaderboard",
    status_code=status.HTTP_200_OK,
    summary="Get EcoPoints leaderboard",
    description="Get top users by EcoPoints (public leaderboard).",
)
async def get_leaderboard(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    Get top users by EcoPoints.

    Returns a leaderboard of users with the most EcoPoints.
    Only returns name and points (no sensitive data).
    """
    result = await db.execute(
        select(User)
        .where(User.deleted_at.is_(None))  # Exclude soft-deleted users
        .order_by(desc(User.eco_points))
        .limit(limit)
    )
    users = result.scalars().all()

    return {
        "leaderboard": [
            {
                "rank": idx + 1,
                "name": user.name,
                "eco_points": user.eco_points,
            }
            for idx, user in enumerate(users)
        ],
        "total": len(users),
    }


@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    summary="Get EcoPoints statistics",
    description="Get overall EcoPoints statistics including total points awarded.",
)
async def get_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get overall EcoPoints statistics for the authenticated user.

    Returns total points earned, total transactions, and user's rank.
    """
    # Get total points earned (sum of positive transactions)
    result = await db.execute(
        select(func.sum(EcoPointTransaction.points))
        .where(
            EcoPointTransaction.user_id == current_user.user_id,
            EcoPointTransaction.points > 0
        )
    )
    total_earned = result.scalar() or 0

    # Get transaction count
    result = await db.execute(
        select(func.count(EcoPointTransaction.transaction_id))
        .where(EcoPointTransaction.user_id == current_user.user_id)
    )
    transaction_count = result.scalar() or 0

    # Get user's rank
    result = await db.execute(
        select(func.count(User.user_id))
        .where(
            User.eco_points > current_user.eco_points,
            User.deleted_at.is_(None)
        )
    )
    rank = result.scalar() + 1  # +1 because count gives number of users ahead

    return {
        "current_balance": current_user.eco_points,
        "total_earned": int(total_earned),
        "total_transactions": transaction_count,
        "rank": rank,
        "pickups_completed": transaction_count,  # Assuming 1 transaction per pickup for now
    }
