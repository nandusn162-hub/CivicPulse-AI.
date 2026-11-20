"""
backend/app/models/repair.py
Repair interventions and verification outcomes.
"""
import uuid
import enum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from typing import Optional


class RepairStatus(str, enum.Enum):
    PLANNED = "planned"
    MATERIALS_ORDERED = "materials_ordered"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class VerificationOutcome(str, enum.Enum):
    PENDING = "pending"
    VERIFIED_FIXED = "verified_fixed"
    PARTIALLY_FIXED = "partially_fixed"
    NOT_FIXED = "not_fixed"
    REOPENED = "reopened"


class RepairIntervention(Base, TimestampMixin):
    __tablename__ = "repair_interventions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    complaint: Mapped["Complaint"] = relationship(  # noqa: F821
        "Complaint", back_populates="repair_interventions"
    )

    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    lead_officer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    status: Mapped[RepairStatus] = mapped_column(
        Enum(RepairStatus, name="repair_status"),
        default=RepairStatus.PLANNED,
        nullable=False,
        index=True,
    )
    verification_outcome: Mapped[VerificationOutcome] = mapped_column(
        Enum(VerificationOutcome, name="verification_outcome"),
        default=VerificationOutcome.PENDING,
        nullable=False,
        index=True,
    )

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    work_order_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    contractor_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    planned_start_date: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_start_date: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_end_date: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end_date: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=True), nullable=True)

    estimated_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    before_photos: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    after_photos: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    materials_used: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    verified_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    verified_at: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    community_satisfaction_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    __table_args__ = (
        Index("ix_repair_complaint_status", "complaint_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<RepairIntervention id={self.id} status={self.status}>"