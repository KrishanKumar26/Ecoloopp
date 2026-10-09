"""
SQLAlchemy models for EcoLoop database schema.
Matches DATABASE.md specification exactly.
"""

import enum
import uuid
from datetime import datetime, timedelta
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, Numeric,
    DateTime, Enum, ForeignKey, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


# Enums matching DATABASE.md specifications
class UserRole(str, enum.Enum):
    """User role enum: user, collector, admin"""
    USER = "user"
    COLLECTOR = "collector"
    ADMIN = "admin"


class PickupStatus(str, enum.Enum):
    """Pickup status enum: pending → accepted → in_transit → completed | cancelled"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class User(Base):
    """
    User accounts table.
    Supports users, collectors, and admins with role-based access.
    """
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True)
    password_hash = Column(Text, nullable=False)
    role = Column(
        Enum(UserRole, values_callable=lambda enum_cls: [member.value for member in enum_cls]),
        nullable=False,
        default=UserRole.USER,
        index=True
    )
    eco_points = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    collector = relationship("Collector", back_populates="user", uselist=False)
    classifications = relationship("Classification", back_populates="user")
    pickups = relationship("Pickup", back_populates="user", foreign_keys="Pickup.user_id")
    transactions = relationship("EcoPointTransaction", back_populates="user")

    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"


class Collector(Base):
    """
    Certified recyclers and pickup agents.
    Linked to a user account with additional business information.
    """
    __tablename__ = "collectors"

    collector_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, unique=True)
    business_name = Column(String(255), nullable=False)
    license_number = Column(String(100), unique=True, nullable=True)
    address = Column(Text, nullable=False)
    lat = Column(Numeric(9, 6), nullable=False)
    lng = Column(Numeric(9, 6), nullable=False)
    rating = Column(Numeric(2, 1), nullable=False, default=0.0)
    accepted_categories = Column(ARRAY(Text), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="collector")
    slots = relationship("RecyclerSlot", back_populates="collector")
    pickups = relationship("Pickup", back_populates="collector", foreign_keys="Pickup.collector_id")

    # Composite index on lat/lng for location-based queries (not GiST since PostGIS not installed)
    __table_args__ = (
        Index('idx_collectors_location', 'lat', 'lng'),
    )

    def __repr__(self):
        return f"<Collector {self.business_name}>"


class Classification(Base):
    """
    AI e-waste classification results.
    Stores AI output including category, confidence, safety tips, and image URLs.
    """
    __tablename__ = "classifications"

    classification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    confidence_score = Column(Numeric(4, 3), nullable=False)  # 0.000-1.000
    safety_tips = Column(ARRAY(Text), nullable=False)
    estimated_weight_kg = Column(Numeric(5, 2), nullable=True)
    raw_label = Column(String(255), nullable=False)
    image_urls = Column(ARRAY(Text), nullable=False)
    user_confirmed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="classifications")
    pickup = relationship("Pickup", back_populates="classification", uselist=False)

    def __repr__(self):
        return f"<Classification {self.category} (confidence: {self.confidence_score})>"


class Pickup(Base):
    """
    Pickup requests and tracking.
    Manages the complete pickup lifecycle from creation to completion with OTP verification.
    """
    __tablename__ = "pickups"

    pickup_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    collector_id = Column(UUID(as_uuid=True), ForeignKey("collectors.collector_id"), nullable=True, index=True)
    classification_id = Column(UUID(as_uuid=True), ForeignKey("classifications.classification_id"), nullable=True)
    item_description = Column(Text, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Address components
    address_street = Column(String(255), nullable=False)
    address_city = Column(String(100), nullable=False)
    address_state = Column(String(100), nullable=False)
    address_pincode = Column(String(20), nullable=False)
    address_lat = Column(Numeric(9, 6), nullable=False)
    address_lng = Column(Numeric(9, 6), nullable=False)

    # OTP for verification - stored as plain text since trust auth is used locally
    # In production, consider hashing OTPs
    otp = Column(String(6), nullable=False)
    otp_expires_at = Column(DateTime(timezone=True), nullable=False)

    status = Column(
        Enum(PickupStatus, values_callable=lambda enum_cls: [member.value for member in enum_cls]),
        nullable=False,
        default=PickupStatus.PENDING,
        index=True
    )
    cancellation_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="pickups", foreign_keys=[user_id])
    collector = relationship("Collector", back_populates="pickups", foreign_keys=[collector_id])
    classification = relationship("Classification", back_populates="pickup")
    transaction = relationship("EcoPointTransaction", back_populates="pickup", uselist=False)
    slot = relationship("RecyclerSlot", back_populates="pickup", uselist=False)

    def is_otp_valid(self, provided_otp: str) -> bool:
        """
        Validate OTP against stored value and expiry time.
        Should be called in application logic, not exposed in API.
        """
        from datetime import datetime, timezone
        if datetime.now(timezone.utc) > self.otp_expires_at:
            return False
        return self.otp == provided_otp

    def __repr__(self):
        return f"<Pickup {self.pickup_id} ({self.status.value})>"


class EcoPointTransaction(Base):
    """
    EcoPoints transaction audit log.
    Immutable record of all point awards and redemptions.
    """
    __tablename__ = "eco_point_transactions"

    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    pickup_id = Column(UUID(as_uuid=True), ForeignKey("pickups.pickup_id"), nullable=True, unique=True)
    points = Column(Integer, nullable=False)  # Positive = earned, Negative = spent
    reason = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="transactions")
    pickup = relationship("Pickup", back_populates="transaction")

    def __repr__(self):
        return f"<Transaction {self.points} points for {self.reason}>"


class RecyclerSlot(Base):
    """
    Available pickup time slots for collectors.
    Manages collector availability and booking status.
    """
    __tablename__ = "recycler_slots"

    slot_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collector_id = Column(UUID(as_uuid=True), ForeignKey("collectors.collector_id"), nullable=False, index=True)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=False)
    is_booked = Column(Boolean, nullable=False, default=False)
    pickup_id = Column(UUID(as_uuid=True), ForeignKey("pickups.pickup_id"), nullable=True, unique=True)

    # Relationships
    collector = relationship("Collector", back_populates="slots")
    pickup = relationship("Pickup", back_populates="slot")

    # Constraint: ends_at must be after starts_at
    __table_args__ = (
        CheckConstraint('ends_at > starts_at', name='check_slot_time_range'),
    )

    def __repr__(self):
        status = "booked" if self.is_booked else "available"
        return f"<RecyclerSlot {self.starts_at} - {self.ends_at} ({status})>"
