"""File storage service — validates and persists uploaded files."""
from __future__ import annotations

import hashlib
import mimetypes
import os
import uuid
from pathlib import Path
from typing import Optional

import aiofiles
from fastapi import UploadFile

from app.core.config import settings

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "video/mp4",
    "audio/wav",
    "audio/mpeg",
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class FileValidationError(ValueError):
    """Raised when a file fails validation."""


async def save_upload(upload: UploadFile) -> dict:
    """
    Validate and persist an uploaded file.

    Returns a dict with keys:
        file_name, mime_type, file_size_bytes, storage_path, file_url
    """
    # Read in chunks, enforce size limit
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await upload.read(64 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_FILE_SIZE_BYTES:
            raise FileValidationError(
                f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB."
            )
        chunks.append(chunk)

    content = b"".join(chunks)

    # Validate MIME type
    content_type = upload.content_type or ""
    if ";" in content_type:
        content_type = content_type.split(";")[0].strip()

    if content_type not in ALLOWED_MIME_TYPES:
        raise FileValidationError(
            f"Unsupported file type: {content_type}. "
            f"Allowed: {', '.join(sorted(ALLOWED_MIME_TYPES))}."
        )

    # Build a safe storage path
    ext = mimetypes.guess_extension(content_type) or ""
    unique_name = f"{uuid.uuid4().hex}{ext}"
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / unique_name

    async with aiofiles.open(dest, "wb") as f:
        await f.write(content)

    return {
        "file_name": upload.filename or unique_name,
        "mime_type": content_type,
        "file_size_bytes": total,
        "storage_path": str(dest),
        "file_url": get_file_url(unique_name),
        "checksum_sha256": hashlib.sha256(content).hexdigest(),
    }


def get_file_url(storage_filename: str) -> str:
    """Return the publicly accessible URL for a stored file."""
    base = getattr(settings, "UPLOAD_BASE_URL", "").rstrip("/")
    if not base:
        base = f"{settings.BASE_URL}/uploads"
    return f"{base}/{storage_filename}"
