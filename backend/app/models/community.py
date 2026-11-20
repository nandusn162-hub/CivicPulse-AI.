"""
backend/app/models/community.py
Community confirmations and comments on complaints.
"""
import uuid
import enum

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, SoftDeleteMixin
from typing import Optional


class ConfirmationType(str, enum.Enum):
    CONFIRMS_ISSUE = "confirms_issue"
    ISSUE_RESOLVED = "issue_resolved"
    DIFFERENT_ISSUE = "different_issue"
    FALSE_REPORT = "false_report"


class CommunityConfirmation(Base, TimestampMixin):
    __tablename__ = "community_confirmations"

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
        "Complaint", back_populates="community_confirmations"
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user: Mapped["User"] = relationship("User", back_populates="community_confirmations")  # noqa: F821

    confirmation_type: Mapped[ConfirmationType] = mapped_column(
        Enum(ConfirmationType, name="confirmation_type"),
        default=ConfirmationType.CONFIRMS_ISSUE,
        nullable=False,
    )
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_community_conf_complaint_user", "complaint_id", "user_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<CommunityConfirmation id={self.id} type={self.confirmation_type}>"


class Comment(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    complaint: Mapped["Complaint"] = relationship("Complaint", back_populates="comments")  # noqa: F821

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    author: Mapped["User"] = relationship("User", back_populates="comments")  # noqa: F821

    parent_comment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("comments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    replies: Mapped[list["Comment"]] = relationship(
        "Comment", foreign_keys=[parent_comment_id]
    )

    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_official: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    upvote_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        Index("ix_comments_complaint_created", "complaint_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Comment id={self.id}>"
