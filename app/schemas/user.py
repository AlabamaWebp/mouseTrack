"""Pydantic schemas for user-related endpoints."""

from datetime import datetime
from pydantic import BaseModel


class UserResponse(BaseModel):
    """User response schema."""
    id: str
    external_id: str | None = None
    created_at: datetime
