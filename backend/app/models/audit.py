"""
backend/app/models/audit.py
Append-only audit event log. No UPDATE or DELETE allowed by application code.
"""
import uuid
import enum

from sqlalchemy import Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from typing import Optional


class AuditAction(str, enum.Enum):
    # Auth
    USER_REGISTERED = "user_registered"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PASSWORD_CHANGED = "password_changed"
    # Complaints
    COMPLAINT_CREATED = "complaint_created"
    COMPLAINT_UPDATED = "complaint_updated"
    COMPLAINT_STATUS_CHANGED = "complaint_status_changed"
    COMPLAINT_ASSIGNED = "complaint_assigned"
    COMPLAINT_RESOLVED = "complaint_resolved"
    COMPLAINT_REJECTED = "complaint_rejected"
    COMPLAINT_DELETED = "complaint_deleted"
    # Inspections
    INSPECTION_CREATED = "inspection_created"
    INSPECTION_COMPLETED = "inspection_completed"
    # Repair
    REPAIR_CREATED = "repair_created"
    REPAIR_UPDATED = "repair_updated"
    REPAIR_VERIFIED = "repair_verified"
    # Admin
    USER_ROLE_CHANGED = "user_role_changed"
    DEPARTMENT_CREATED = "department_created"
    DEPARTMENT_UPDATED = "department_updated"
    # Data export
    DATA_EXPORTED = "data_exported"
    REPORT_GENERATED = "report_generated"


class AuditEvent(Base, TimestampMixin):
    """
    Append-only audit log.
    Application code must NEVER UPDATE or DELETE rows in this table.
    Use PostgreSQL row-level security or triggers to enforce this if needed.
    """
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction, name="audit_action"), nullable=False, index=True
    )

    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    actor: Mapped[Optional["User"]] = relationship("User", back_populates="audit_events")  # noqa: F821

    # The entity being acted upon
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)

    # What changed
    before_state: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    after_state: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    extra_context: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)

    __table_args__ = (
        Index("ix_audit_events_entity", "entity_type", "entity_id"),
        Index("ix_audit_events_actor_action", "actor_id", "action"),
    )

    def __repr__(self) -> str:
        return f"<AuditEvent id={self.id} action={self.action}>"