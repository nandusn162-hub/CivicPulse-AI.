"""
backend/app/models/department.py
City/municipal department that handles complaint resolution.
"""
import uuid

from sqlalchemy import String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, SoftDeleteMixin
from typing import Optional


class Department(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    head_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    complaints: Mapped[list["Complaint"]] = relationship(  # noqa: F821
        "Complaint", back_populates="assigned_department"
    )
    inspections: Mapped[list["Inspection"]] = relationship(  # noqa: F821
        "Inspection", back_populates="department"
    )

    def __repr__(self) -> str:
        return f"<Department id={self.id} code={self.code}>"