"""
backend/app/models/predictions.py
AI-generated infrastructure failure / issue predictions.
"""
import uuid
import enum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from typing import Optional


class PredictionStatus(str, enum.Enum):
    ACTIVE = "active"
    CONFIRMED = "confirmed"     # prediction came true
    EXPIRED = "expired"         # past valid_until without confirmation
    DISMISSED = "dismissed"     # manually dismissed by an admin


class PredictionType(str, enum.Enum):
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    RECURRENCE = "recurrence"
    SEASONAL_HOTSPOT = "seasonal_hotspot"
    MAINTENANCE_DUE = "maintenance_due"
    BUDGET_OVERRUN = "budget_overrun"


class Prediction(Base, TimestampMixin):
    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    prediction_type: Mapped[PredictionType] = mapped_column(
        Enum(PredictionType, name="prediction_type"), nullable=False, index=True
    )
    status: Mapped[PredictionStatus] = mapped_column(
        Enum(PredictionStatus, name="prediction_status"),
        default=PredictionStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    # What the prediction is about
    ward_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wards.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("infrastructure_assets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Prediction details
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    expected_occurrence_date: Mapped[Optional[Any]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    valid_until: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Model metadata
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    model_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    feature_importance: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    input_features: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    recommendations: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    # Estimated impact
    estimated_affected_population: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estimated_repair_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Outcome tracking
    confirmed_at: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmed_complaint_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="SET NULL"),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_predictions_ward_type_status", "ward_id", "prediction_type", "status"),
    )

    def __repr__(self) -> str:
        return f"<Prediction id={self.id} type={self.prediction_type}>"