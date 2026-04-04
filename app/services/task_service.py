"""Task service for managing task lifecycle."""

from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus


class TaskService:
    """Service for managing tasks."""

    @staticmethod
    def get_task(db: Session, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def get_pending_tasks(db: Session) -> List[Task]:
        """Get all pending tasks."""
        return db.query(Task).filter(Task.status == TaskStatus.PENDING).order_by(Task.created_at).all()

    @staticmethod
    def get_processing_task(db: Session) -> Optional[Task]:
        """Get the currently processing task."""
        return db.query(Task).filter(Task.status == TaskStatus.PROCESSING).first()

    @staticmethod
    def update_task_status(
        db: Session,
        task_id: str,
        status: TaskStatus,
        result: Optional[dict] = None,
        error_message: Optional[str] = None
    ) -> Optional[Task]:
        """Update task status and optionally set result or error."""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None

        task.status = status
        if result is not None:
            task.result = result
        if error_message is not None:
            task.error_message = error_message
        if status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_recently_completed(db: Session, limit: int = 5) -> List[Task]:
        """Get recently completed tasks."""
        return (
            db.query(Task)
            .filter(Task.status == TaskStatus.COMPLETED)
            .order_by(Task.completed_at.desc())
            .limit(limit)
            .all()
        )
