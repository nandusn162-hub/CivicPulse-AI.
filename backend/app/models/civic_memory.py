"""
backend/app/models/civic_memory.py
Civic memory layer: recurrence events, risk assessments, repeat-failure zones.
"""
import uuid
import enum

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from typing import Optional, Any
from datetime import datetime


class RiskLevel(str, enum.Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecurrenceEvent(Base, TimestampMixin):
    """Links a new complaint occurrence to an earlier complaint at the same location."""
    __tablename__ = "recurrence_events"

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
        "Complaint", back_populates="recurrence_events"
    )

    original_complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    occurrence_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    days_since_last_occurrence: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    similarity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<RecurrenceEvent id={self.id} occurrence={self.occurrence_number}>"


class RiskAssessment(Base, TimestampMixin):
    """AI-generated risk forecast for a ward or infrastructure zone."""
    __tablename__ = "risk_assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    ward_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wards.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    ward: Mapped[Optional["Ward"]] = relationship("Ward", back_populates="risk_assessments")  # noqa: F821

    asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("infrastructure_assets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="risk_level"),
        default=RiskLevel.MEDIUM,
        nullable=False,
        index=True,
    )
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    predicted_failure_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    factors: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    recommendations: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    valid_until: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<RiskAssessment id={self.id} level={self.risk_level}>"


class RepeatFailureZone(Base, TimestampMixin):
    """PostGIS polygon clustering repeat complaints into hotspot zones."""
    __tablename__ = "repeat_failure_zones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    zone_polygon: Mapped[Any] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326), nullable=False
    )
    centroid: Mapped[Optional[Any]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )

    radius_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    complaint_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    recurrence_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_days_between_failures: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    ward_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wards.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, index=True)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_rfz_zone_polygon_gist", "zone_polygon", postgresql_using="gist"),
        Index("ix_rfz_centroid_gist", "centroid", postgresql_using="gist"),
    )

    def __repr__(self) -> str:
        return f"<RepeatFailureZone id={self.id} name={self.name}>"