"""Pydantic schemas for task-related API endpoints."""

from datetime import datetime, timezone
from typing import Optional, Any, List
from pydantic import BaseModel, Field

from app.models.task import TaskStatus


class TaskResponse(BaseModel):
    """Response for video upload."""
    task_id: str
    status: TaskStatus
    message: str
    is_duplicate: bool = False
    result: Optional[Any] = None


class TaskStatusResponse(BaseModel):
    """Response for task status check."""
    task_id: str
    status: TaskStatus
    video_filename: str
    progress: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class TaskResultResponse(BaseModel):
    """Response for task result check."""
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None


class QueueItem(BaseModel):
    """Item in the queue for WebSocket broadcast."""
    task_id: str
    filename: str
    user_id: str
    progress: Optional[int] = None


class CurrentProcessing(BaseModel):
    """Currently processing task info."""
    task_id: str
    filename: str
    user_id: str
    progress: Optional[int] = 0


class QueueStatusResponse(BaseModel):
    """WebSocket queue status update."""
    type: str = "queue_update"
    nn_status: str = Field(..., description="busy or idle")
    current_processing: Optional[CurrentProcessing] = None
    pending_queue: List[QueueItem] = []
    recently_completed: List[QueueItem] = []


class NNStatusChange(BaseModel):
    """WebSocket NN status change message."""
    type: str = "nn_status_change"
    status: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TaskCompletedMessage(BaseModel):
    """WebSocket task completed message."""
    type: str = "task_completed"
    task_id: str
    filename: str
