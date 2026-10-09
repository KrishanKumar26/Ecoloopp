"""
Classification router for e-waste identification.
Handles item classification requests (with or without images).
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from decimal import Decimal

from database import get_db
from models import Classification, User
from dependencies import get_current_active_user
from classifier import classify_ewaste, get_supported_categories
import uuid


router = APIRouter(
    prefix="/api/classify",
    tags=["Classification"],
)


# Allowed file types for image upload
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    summary="Classify e-waste item",
    description="Classify an e-waste item by name. Optionally upload an image (future ML integration). "
                "Returns category, confidence score, safety tips, and handling guidance. "
                "NOTE: Currently uses a baseline keyword classifier, not a trained ML model.",
)
async def classify_item(
    item_name: str = Form(..., description="Name or description of the e-waste item"),
    image: Optional[UploadFile] = File(None, description="Optional: Photo of the item (JPEG/PNG, max 10MB)"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Classify an e-waste item and store the result.

    This endpoint:
    1. Validates item name and optional image
    2. Classifies the item using baseline keyword matching
    3. Stores classification result in database
    4. Returns classification with safety tips and handling guidance

    Image Upload (optional):
    - Currently stored but not used for classification
    - File types: JPEG, PNG, WEBP
    - Max size: 10 MB
    - Prepared for future ML model integration

    Authentication:
    - Requires valid JWT token
    - Classification is linked to authenticated user

    Args:
        item_name: Description of the e-waste item (required)
        image: Optional image file (for future ML classification)
        current_user: Authenticated user (injected)
        db: Database session (injected)

    Returns:
        Classification result with category, confidence, safety tips, etc.
    """

    # Validate item name
    if not item_name or not item_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item name is required"
        )

    # Validate image if provided
    image_urls = []
    if image:
        # Check file size
        content = await image.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum of {MAX_FILE_SIZE / (1024 * 1024):.0f} MB"
            )

        # Check file type
        if not is_allowed_file(image.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # In production, upload to S3/Cloudinary
        # For now, store placeholder URL
        image_filename = f"{uuid.uuid4()}_{image.filename}"
        image_urls.append(f"/uploads/{image_filename}")

        # Note: Actual file upload to storage would happen here
        # await upload_to_storage(content, image_filename)

    # Classify the item using baseline classifier
    classification_result = classify_ewaste(item_name)

    # Create classification record
    new_classification = Classification(
        user_id=current_user.user_id,
        category=classification_result["category"],
        confidence_score=Decimal(str(classification_result["confidence_score"])),
        safety_tips=classification_result["safety_tips"],
        estimated_weight_kg=Decimal(str(classification_result["estimated_weight_kg"])) if classification_result["estimated_weight_kg"] else None,
        raw_label=item_name,
        image_urls=image_urls if image_urls else ["no_image_provided"],
        user_confirmed=False,
    )

    try:
        db.add(new_classification)
        await db.commit()
        await db.refresh(new_classification)

        # Return classification result
        # Note: Return both 'confidence' (frontend) and 'confidence_score' (backend) for compatibility
        confidence = float(classification_result["confidence_score"])

        return {
            "classification_id": str(new_classification.classification_id),
            "item_name": item_name,  # Frontend expects 'item_name'
            "category": classification_result["category"],
            "confidence": confidence,  # Frontend field name
            "confidence_score": confidence,  # Backend field name (keep for compatibility)
            "safety_tips": classification_result["safety_tips"],
            "estimated_weight_kg": float(classification_result["estimated_weight_kg"]) if classification_result["estimated_weight_kg"] else None,
            "special_care_warning": classification_result.get("warning"),  # Frontend field name
            "special_care_needed": classification_result["special_care_needed"],  # Backend field name
            "classifier_type": classification_result["classifier_type"],
            "warning": classification_result.get("warning"),  # Keep for backward compatibility
            "raw_label": item_name,
            "image_url": image_urls[0] if image_urls else None,  # Frontend expects single URL
            "image_uploaded": image is not None,
            "classified_at": new_classification.created_at.isoformat(),  # Frontend field name
            "created_at": new_classification.created_at.isoformat(),  # Backend field name
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store classification: {str(e)}"
        )


@router.get(
    "/categories",
    status_code=status.HTTP_200_OK,
    summary="Get supported e-waste categories",
    description="Returns a list of all supported e-waste categories.",
)
async def get_categories():
    """Get list of supported e-waste categories."""
    categories = get_supported_categories()
    return {
        "categories": categories,
        "total": len(categories),
    }


@router.get(
    "/history",
    status_code=status.HTTP_200_OK,
    summary="Get user's classification history",
    description="Returns all classifications made by the authenticated user.",
)
async def get_classification_history(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 10,
):
    """
    Get user's classification history.

    Args:
        current_user: Authenticated user (injected)
        db: Database session (injected)
        limit: Maximum number of results (default: 10)

    Returns:
        List of user's past classifications
    """
    from sqlalchemy import select, desc

    result = await db.execute(
        select(Classification)
        .where(Classification.user_id == current_user.user_id)
        .order_by(desc(Classification.created_at))
        .limit(limit)
    )
    classifications = result.scalars().all()

    return {
        "classifications": [
            {
                "classification_id": str(c.classification_id),
                "item_name": c.raw_label,  # Frontend field name
                "category": c.category,
                "confidence": float(c.confidence_score),  # Frontend field name
                "confidence_score": float(c.confidence_score),  # Backend field name (keep for compatibility)
                "safety_tips": c.safety_tips,
                "estimated_weight_kg": float(c.estimated_weight_kg) if c.estimated_weight_kg else None,
                "raw_label": c.raw_label,
                "user_confirmed": c.user_confirmed,
                "classified_at": c.created_at.isoformat(),  # Frontend field name
                "created_at": c.created_at.isoformat(),  # Backend field name
            }
            for c in classifications
        ],
        "total": len(classifications),
    }
