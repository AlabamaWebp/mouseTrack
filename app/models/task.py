"""Task database model."""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.dialects.sqlite import CHAR

from app.database import Base


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(Base):
    """Task model for tracking video processing jobs."""

    __tablename__ = "tasks"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    video_hash = Column(String(64), nullable=False, unique=True, index=True)
    video_path = Column(String, nullable=False)
    video_filename = Column(String, nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    result = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Task(id={self.id}, status={self.status}, filename={self.video_filename})>"
