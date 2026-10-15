"""Private File Storage Abstraction.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 7.2 & Section 16.
Prevents path traversal, sanitizes filenames, and stores files using opaque UUIDs.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile

from backend.app.core.config import settings


class FileStorage:
    """Secure private file storage service."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root = Path(root_dir or settings.FILE_STORAGE_ROOT).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    async def save_upload(
        self,
        upload_file: UploadFile,
        subfolder: str = "inspections",
    ) -> Tuple[str, str, int]:
        """Save an uploaded file safely and return (storage_rel_path, sanitized_filename, byte_size)."""
        clean_filename = os.path.basename(upload_file.filename or "uploaded_file")
        ext = os.path.splitext(clean_filename)[1].lower()

        # Generate unique storage filename
        stored_name = f"{uuid.uuid4().hex}{ext}"
        folder_path = self.root / subfolder
        folder_path.mkdir(parents=True, exist_ok=True)

        full_path = folder_path / stored_name

        content = await upload_file.read()
        byte_size = len(content)

        with open(full_path, "wb") as f:
            f.write(content)

        rel_path = str(full_path.relative_to(self.root))
        return rel_path, clean_filename, byte_size

    def get_full_path(self, rel_path: str) -> Path:
        """Resolve relative storage path and verify it remains within root."""
        resolved = (self.root / rel_path).resolve()
        if not str(resolved).startswith(str(self.root)):
            raise PermissionError("Path traversal attempt detected.")
        return resolved

    def read_bytes(self, rel_path: str) -> bytes:
        """Read file contents into memory."""
        full_path = self.get_full_path(rel_path)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {rel_path}")
        with open(full_path, "rb") as f:
            return f.read()

    def delete_file(self, rel_path: str) -> bool:
        """Remove file from storage."""
        try:
            full_path = self.get_full_path(rel_path)
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception:
            return False


file_storage = FileStorage()
