"""FastAPI application entry point."""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db, init_db, SessionLocal
from app.api import upload, tasks, auth
from app.models.task import TaskStatus
from app.services.task_service import TaskService
from app.services.nn_processor import process_video
from app.services.websocket_manager import manager

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    init_db()
    print("Database initialized")

    # Start background task processor
    task = asyncio.create_task(process_queue())
    yield
    # Shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Video Processing Service",
    description="Backend service for video processing with neural networks",
    version="0.1.0",
    lifespan=lifespan
)

# Include routers
app.include_router(upload.router)
app.include_router(tasks.router)
app.include_router(auth.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Video Processing Service",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.websocket("/ws/queue")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time queue status updates.

    Connects clients to receive broadcast updates about:
    - NN processing status (busy/idle)
    - Currently processing file
    - Pending queue
    - Recently completed tasks
    """
    await manager.connect(websocket)
    try:
        # Send initial status
        db = SessionLocal()
        try:
            processing_task = TaskService.get_processing_task(db)
            pending_tasks = TaskService.get_pending_tasks(db)
            recent_tasks = TaskService.get_recently_completed(db)

            nn_status = "busy" if processing_task else "idle"
            current_processing = None
            if processing_task:
                current_processing = {
                    "task_id": processing_task.id,
                    "filename": processing_task.video_filename,
                    "user_id": processing_task.user_id,
                    "progress": 50
                }

            pending_queue = [
                {
                    "task_id": t.id,
                    "filename": t.video_filename,
                    "user_id": t.user_id
                }
                for t in pending_tasks
            ]

            recently_completed = [
                {
                    "task_id": t.id,
                    "filename": t.video_filename,
                    "user_id": t.user_id
                }
                for t in recent_tasks[:5]
            ]

            await manager.broadcast_queue_status(
                nn_status=nn_status,
                current_processing=current_processing,
                pending_queue=pending_queue,
                recently_completed=recently_completed
            )
        finally:
            db.close()

        # Keep connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def process_queue():
    """
    Background task that processes the queue of pending videos.

    Picks up pending tasks one at a time and processes them through
    the neural network processor.
    """
    while True:
        try:
            db = SessionLocal()
            try:
                # Get next pending task
                pending_tasks = TaskService.get_pending_tasks(db)
                if not pending_tasks:
                    await asyncio.sleep(1)
                    continue

                task = pending_tasks[0]

                # Update status to processing
                TaskService.update_task_status(db, task.id, TaskStatus.PROCESSING)

                # Broadcast status change
                await manager.broadcast_nn_status_change("busy")
                await manager.broadcast_queue_status(
                    nn_status="busy",
                    current_processing={
                        "task_id": task.id,
                        "filename": task.video_filename,
                        "user_id": task.user_id,
                        "progress": 0
                    },
                    pending_queue=[
                        {
                            "task_id": t.id,
                            "filename": t.video_filename,
                            "user_id": t.user_id
                        }
                        for t in pending_tasks[1:]
                    ]
                )

                # Process the video
                result = await process_video(task.video_path)

                # Update task with result
                TaskService.update_task_status(
                    db, task.id, TaskStatus.COMPLETED, result=result
                )

                # Broadcast completion
                await manager.broadcast_task_completed(task.id, task.video_filename)
                await manager.broadcast_nn_status_change("idle")

            finally:
                db.close()

        except Exception as e:
            print(f"Error processing queue: {e}")
            await asyncio.sleep(5)
