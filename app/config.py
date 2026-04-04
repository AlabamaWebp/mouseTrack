"""Application configuration settings."""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Storage
    VIDEO_STORAGE_PATH: str = "./videos"
    MAX_FILE_SIZE_MB: int = 500
    ALLOWED_VIDEO_EXTENSIONS: str = "mp4,avi,mov,mkv,webm"

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # Processing
    NN_PROCESSING_TIMEOUT_SECONDS: int = 3600

    @property
    def allowed_video_extensions(self) -> List[str]:
        """Get list of allowed video file extensions."""
        return [ext.strip() for ext in self.ALLOWED_VIDEO_EXTENSIONS.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
