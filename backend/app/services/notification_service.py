"""Notification service."""
from __future__ import annotations

from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


async def send_notification(
    db: AsyncSession,
    *,
    user_id: UUID,
    title: str,
    body: str,
    notification_type: str = "info",
    reference_entity_type: Optional[str] = None,
    reference_entity_id: Optional[UUID] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Create a Notification record for a user."""
    from app.models.notifications import Notification

    notif = Notification(
        user_id=user_id,
        title=title,
        body=body,
        notification_type=notification_type,
        reference_entity_type=reference_entity_type,
        reference_entity_id=reference_entity_id,
        metadata=metadata or {},
        is_read=False,
    )
    db.add(notif)
    await db.flush()
