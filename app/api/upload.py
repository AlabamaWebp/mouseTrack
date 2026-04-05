"""Upload video endpoint."""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.task import TaskResponse
from app.services.upload_service import UploadService
from app.services.websocket_manager import manager

router = APIRouter(prefix="/api/v1/videos", tags=["videos"])


@router.post("/upload", response_model=TaskResponse)
async def upload_video(
    video: UploadFile = File(...),
    user_id: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Upload a video file for processing.

    - **video**: Video file to upload
    - **user_id**: User identifier (will be replaced by auth token in future)

    Returns a task_id that can be used to check status.
    """
    try:
        result = await UploadService.process_upload(video, user_id, db)

        # If not a duplicate, broadcast queue update
        if not result["is_duplicate"]:
            await manager.broadcast_queue_status(
                nn_status="busy" if result["status"] == "pending" else "idle",
                pending_queue=[
                    {
                        "task_id": result["task_id"],
                        "filename": video.filename or "unknown",
                        "user_id": user_id,
                    }
                ],
            )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
