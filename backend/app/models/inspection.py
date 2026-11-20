"""
backend/app/models/inspection.py
Field inspection records linked to complaints.
"""
import uuid
import enum

from sqlalchemy import Enum, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime

from .base import Base, TimestampMixin
from typing import Optional, Any


class InspectionStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class InspectionFindings(str, enum.Enum):
    CONFIRMED = "confirmed"
    NOT_FOUND = "not_found"
    DIFFERENT_ISSUE = "different_issue"
    ALREADY_FIXED = "already_fixed"
    ESCALATION_NEEDED = "escalation_needed"


class Inspection(Base, TimestampMixin):
    __tablename__ = "inspections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    complaint: Mapped["Complaint"] = relationship("Complaint", back_populates="inspections")  # noqa: F821

    inspector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    inspector: Mapped["User"] = relationship("User")  # noqa: F821

    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="inspections")  # noqa: F821

    status: Mapped[InspectionStatus] = mapped_column(
        Enum(InspectionStatus, name="inspection_status"),
        default=InspectionStatus.SCHEDULED,
        nullable=False,
        index=True,
    )
    findings: Mapped[Optional[InspectionFindings]] = mapped_column(
        Enum(InspectionFindings, name="inspection_findings"), nullable=True
    )

    scheduled_at: Mapped[Any] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=True), nullable=True)

    location_latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estimated_repair_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    priority_adjustment: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    evidence: Mapped[list["InspectionEvidence"]] = relationship(
        "InspectionEvidence", back_populates="inspection"
    )

    __table_args__ = (
        Index("ix_inspections_complaint_status", "complaint_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<Inspection id={self.id} status={self.status}>"


class InspectionEvidence(Base, TimestampMixin):
    __tablename__ = "inspection_evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    inspection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="evidence")

    evidence_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evidence_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    evidence_file: Mapped["EvidenceFile"] = relationship(  # noqa: F821
        "EvidenceFile", back_populates="inspection_evidence"
    )
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<InspectionEvidence id={self.id}>"