"""Pydantic schemas for evidence files."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "video/mp4",
    "audio/wav",
    "audio/mpeg",
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class EvidenceUpload(BaseModel):
    """Metadata accompanying a multipart upload (body fields)."""
    complaint_id: UUID
    description: Optional[str] = Field(None, max_length=500)


class EvidenceResponse(BaseModel):
    id: UUID
    complaint_id: UUID
    uploader_id: UUID
    file_name: str
    mime_type: str
    file_size_bytes: int
    file_url: str
    description: Optional[str]
    uploaded_at: datetime

    model_config = {"from_attributes": True}
