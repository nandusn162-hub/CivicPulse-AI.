"""Audit event service — append-only event log."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def record_event(
    db: AsyncSession,
    *,
    entity_type: str,
    entity_id: UUID,
    action: str,
    actor_id: Optional[UUID],
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Create an immutable audit event. Never updates existing records."""
    from app.models.audit import AuditEvent  # local import to avoid circular deps

    event = AuditEvent(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor_id=actor_id,
        metadata=metadata or {},
        occurred_at=datetime.now(timezone.utc),
    )
    db.add(event)
    await db.flush()


async def get_complaint_audit_trail(
    db: AsyncSession,
    complaint_id: UUID,
) -> List[Any]:
    """Return ordered list of audit events for a complaint."""
    from app.models.audit import AuditEvent

    result = await db.execute(
        select(AuditEvent)
        .where(
            AuditEvent.entity_type == "complaint",
            AuditEvent.entity_id == complaint_id,
        )
        .order_by(AuditEvent.occurred_at.asc())
    )
    return result.scalars().all()
