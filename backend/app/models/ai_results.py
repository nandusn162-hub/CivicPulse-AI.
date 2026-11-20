"""
backend/app/models/ai_results.py
Stores Gemini / ML analysis outputs for a piece of evidence or a complaint.
"""
import uuid
import enum

from sqlalchemy import Enum, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class AnalysisType(str, enum.Enum):
    IMAGE_CLASSIFICATION = "image_classification"
    SEVERITY_ESTIMATION = "severity_estimation"
    CATEGORY_DETECTION = "category_detection"
    DAMAGE_ASSESSMENT = "damage_assessment"
    LOCATION_VERIFICATION = "location_verification"
    RECURRENCE_DETECTION = "recurrence_detection"
    PRIORITY_SCORING = "priority_scoring"
    REPAIR_COST_ESTIMATION = "repair_cost_estimation"


class AIAnalysisResult(Base, TimestampMixin):
    __tablename__ = "ai_analysis_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    complaint: Mapped["Complaint"] = relationship("Complaint", back_populates="ai_results")  # noqa: F821

    evidence_file_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evidence_files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    evidence_file: Mapped[Optional["EvidenceFile"]] = relationship(
        "EvidenceFile", back_populates="ai_results"
    )

    analysis_type: Mapped[AnalysisType] = mapped_column(
        Enum(AnalysisType, name="analysis_type"), nullable=False, index=True
    )
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    model_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Classification results
    predicted_category: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    severity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    priority_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    estimated_repair_cost_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    estimated_repair_cost_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Full structured output from the model
    raw_response: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Processing metadata
    processing_time_ms: Mapped[Optional[int]] = mapped_column(nullable=True)
    is_valid: Mapped[bool] = mapped_column(default=True, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_ai_results_complaint_type", "complaint_id", "analysis_type"),
    )

    def __repr__(self) -> str:
        return f"<AIAnalysisResult id={self.id} type={self.analysis_type}>"
