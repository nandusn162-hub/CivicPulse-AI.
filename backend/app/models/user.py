"""
backend/app/models/user.py
User account model with role-based access control.
Uses String-based UUID columns for SQLite compatibility.
"""
import uuid
import enum
from typing import Optional

from sqlalchemy import Boolean, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, SoftDeleteMixin


class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    FIELD_INSPECTOR = "field_inspector"
    DEPARTMENT_OFFICER = "department_officer"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(
        String(320), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        default=UserRole.CITIZEN,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ward_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, index=True
    )
    department_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, index=True
    )

    @property
    def phone(self) -> Optional[str]:
        return self.phone_number

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
