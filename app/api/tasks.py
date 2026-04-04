"""Task status and result endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import TaskStatus
from app.schemas.task import TaskStatusResponse, TaskResultResponse
from app.services.task_service import TaskService

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, db: Session = Depends(get_db)):
    """
    Get the current status of a task.

    - **task_id**: The ID of the task to check
    """
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskStatusResponse(
        task_id=task.id,
        status=task.status,
        video_filename=task.video_filename,
        progress=50 if task.status == TaskStatus.PROCESSING else None,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.get("/{task_id}/result", response_model=TaskResultResponse)
async def get_task_result(task_id: str, db: Session = Depends(get_db)):
    """
    Get the result of a completed task.

    - **task_id**: The ID of the task

    Returns 202 if result is not ready yet.
    """
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status == TaskStatus.PENDING:
        return TaskResultResponse(
            task_id=task.id,
            status=task.status,
            error_message=None,
            completed_at=None
        )

    if task.status == TaskStatus.PROCESSING:
        return TaskResultResponse(
            task_id=task.id,
            status=task.status,
            error_message=None,
            completed_at=None
        )

    if task.status == TaskStatus.FAILED:
        return TaskResultResponse(
            task_id=task.id,
            status=task.status,
            error_message=task.error_message,
            completed_at=task.completed_at
        )

    return TaskResultResponse(
        task_id=task.id,
        status=task.status,
        result=task.result,
        completed_at=task.completed_at
    )
