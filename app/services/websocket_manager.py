"""WebSocket connection manager for broadcasting queue status."""

import asyncio
import json
from typing import Dict, List, Set
from fastapi import WebSocket
from datetime import datetime, timezone


class WebSocketManager:
    """Manages WebSocket connections and broadcasts messages to all clients."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accept and store a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        """Send a message to all connected clients."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # Clean up disconnected clients
        self.active_connections -= disconnected

    async def broadcast_queue_status(
        self,
        nn_status: str,
        current_processing: dict | None = None,
        pending_queue: list[dict] | None = None,
        recently_completed: list[dict] | None = None
    ):
        """Broadcast the current queue status to all connected clients."""
        message = {
            "type": "queue_update",
            "nn_status": nn_status,
            "current_processing": current_processing,
            "pending_queue": pending_queue or [],
            "recently_completed": recently_completed or []
        }
        await self.broadcast(message)

    async def broadcast_nn_status_change(self, status: str):
        """Broadcast NN status change (busy/idle)."""
        message = {
            "type": "nn_status_change",
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await self.broadcast(message)

    async def broadcast_task_completed(self, task_id: str, filename: str):
        """Broadcast that a task has been completed."""
        message = {
            "type": "task_completed",
            "task_id": task_id,
            "filename": filename
        }
        await self.broadcast(message)

    @property
    def connection_count(self) -> int:
        """Return the number of active connections."""
        return len(self.active_connections)


# Global WebSocket manager instance
manager = WebSocketManager()
