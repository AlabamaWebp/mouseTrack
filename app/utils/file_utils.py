"""File utility functions for hashing and validation."""

import hashlib
import os
from typing import BinaryIO

from app.config import get_settings

settings = get_settings()


def calculate_file_hash(file: BinaryIO, chunk_size: int = 8192) -> str:
    """Calculate SHA-256 hash of a file."""
    file.seek(0)
    sha256 = hashlib.sha256()
    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            break
        sha256.update(chunk)
    file.seek(0)  # Reset file pointer
    return sha256.hexdigest()


def validate_video_extension(filename: str) -> bool:
    """Check if the file has an allowed video extension."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in settings.allowed_video_extensions


def validate_file_size(file: BinaryIO) -> bool:
    """Check if the file size is within the allowed limit."""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= settings.max_file_size_bytes


def get_safe_filename(filename: str) -> str:
    """Generate a safe filename by removing potentially dangerous characters."""
    # Keep only alphanumeric, dots, hyphens, and underscores
    safe_chars = []
    for char in filename:
        if char.isalnum() or char in ".-_":
            safe_chars.append(char)
    return "".join(safe_chars) or "unnamed_video"
