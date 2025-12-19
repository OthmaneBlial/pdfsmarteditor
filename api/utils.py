import logging
import os
import uuid
from typing import Set

from fastapi import HTTPException, UploadFile

from api.deps import MAX_UPLOAD_MB, TEMP_DIR

logger = logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    return os.path.basename(filename)


def _get_upload_size(upload_file: UploadFile) -> int:
    try:
        upload_file.file.seek(0, os.SEEK_END)
        size = upload_file.file.tell()
        upload_file.file.seek(0)
        return size
    except Exception:
        return 0


def _validate_upload_file(
    upload_file: UploadFile, allowed_types: Set[str], max_mb: int = MAX_UPLOAD_MB
):
    content_type = upload_file.content_type or ""
    if allowed_types and content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{content_type}'. Allowed: {', '.join(sorted(allowed_types))}",
        )

    size_bytes = _get_upload_size(upload_file)
    if size_bytes and size_bytes > max_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large (> {max_mb} MB).")


async def persist_upload_file(
    upload_file: UploadFile, allowed_types: Set[str], prefix: str = ""
) -> str:
    _validate_upload_file(upload_file, allowed_types)
    safe_filename = sanitize_filename(upload_file.filename or "upload.bin")
    storage_name = f"{prefix}{uuid.uuid4()}_{safe_filename}"
    storage_path = os.path.join(TEMP_DIR, storage_name)

    upload_file.file.seek(0)
    content = await upload_file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    with open(storage_path, "wb") as f:
        f.write(content)

    return storage_path
