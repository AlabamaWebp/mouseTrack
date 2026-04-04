"""Upload service for handling video file uploads and deduplication."""

import hashlib
import os
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.task import Task, TaskStatus
from app.utils.file_utils import validate_video_extension, validate_file_size, get_safe_filename

settings = get_settings()


class UploadService:
    """Service for handling video file uploads."""

    @staticmethod
    async def process_upload(
        file: UploadFile,
        user_id: str,
        db: Session
    ) -> dict:
        """
        Process a video upload:
        1. Validate file
        2. Calculate hash for deduplication
        3. Check if video already exists
        4. Save file if new
        5. Create task record
        """
        # Validate file extension
        if not validate_video_extension(file.filename or ""):
            raise ValueError(f"Invalid file type. Allowed: {settings.allowed_video_extensions}")

        # Read file content for hashing and saving
        content = await file.read()

        # Validate file size
        if len(content) > settings.max_file_size_bytes:
            raise ValueError(f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB")

        # Calculate hash
        file_hash = calculate_file_hash_from_bytes(content)

        # Check for duplicate
        existing_task = db.query(Task).filter(Task.video_hash == file_hash).first()
        if existing_task:
            return {
                "task_id": existing_task.id,
                "status": existing_task.status,
                "message": "Video already processed",
                "is_duplicate": True,
                "result": existing_task.result if existing_task.status == TaskStatus.COMPLETED else None
            }

        # Save file
        safe_filename = get_safe_filename(file.filename or "video.mp4")
        file_path = os.path.join(settings.VIDEO_STORAGE_PATH, safe_filename)

        # Ensure storage directory exists
        os.makedirs(settings.VIDEO_STORAGE_PATH, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(content)

        # Create task record
        new_task = Task(
            user_id=user_id,
            video_hash=file_hash,
            video_path=file_path,
            video_filename=safe_filename,
            status=TaskStatus.PENDING
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return {
            "task_id": new_task.id,
            "status": new_task.status,
            "message": "Video uploaded successfully",
            "is_duplicate": False,
            "result": None
        }


def calculate_file_hash_from_bytes(content: bytes) -> str:
    """Calculate SHA-256 hash from bytes."""
    return hashlib.sha256(content).hexdigest()


