"""User database model (placeholder for future authentication)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.sqlite import CHAR

from app.database import Base


class User(Base):
    """User model placeholder for future authentication integration."""

    __tablename__ = "users"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    external_id = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, external_id={self.external_id})>"
