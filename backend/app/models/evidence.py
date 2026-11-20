"""
backend/app/models/evidence.py
Evidence files (photos, videos, documents) attached to complaints.
"""
import uuid
import enum

from sqlalchemy import BigInteger, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from typing import Optional


class EvidenceType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"


class EvidenceFile(Base, TimestampMixin):
    __tablename__ = "evidence_files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    complaint: Mapped["Complaint"] = relationship("Complaint", back_populates="evidence_files")  # noqa: F821

    uploader_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    file_type: Mapped[EvidenceType] = mapped_column(
        Enum(EvidenceType, name="evidence_type"), nullable=False, index=True
    )
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    checksum_sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # For images/video: dimensions, duration
    width: Mapped[Optional[int]] = mapped_column(nullable=True)
    height: Mapped[Optional[int]] = mapped_column(nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(nullable=True)

    # EXIF / embedded location
    exif_latitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    exif_longitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    exif_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    thumbnail_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_primary: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    ai_results: Mapped[list["AIAnalysisResult"]] = relationship(  # noqa: F821
        "AIAnalysisResult", back_populates="evidence_file"
    )
    inspection_evidence: Mapped[list["InspectionEvidence"]] = relationship(  # noqa: F821
        "InspectionEvidence", back_populates="evidence_file"
    )

    __table_args__ = (
        Index("ix_evidence_complaint_primary", "complaint_id", "is_primary"),
    )

    def __repr__(self) -> str:
        return f"<EvidenceFile id={self.id} type={self.file_type}>"