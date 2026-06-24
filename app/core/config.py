from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VoiceLab Studio"
    app_env: str = "development"
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    telegram_bot_token: str = "replace-me"

    database_url: str = "postgresql+asyncpg://voicelab:voicelab@db:5432/voicelab"
    redis_url: str = "redis://redis:6379/0"
    api_base_url: str = "http://api:8000"
    gemini_api_key: str = "replace-me"

    storage_root: Path = Field(default=Path("storage"))
    models_root: Path = Field(default=Path("models"))
    ffmpeg_binary: str = "ffmpeg"
    ffprobe_binary: str = "ffprobe"
    media_subprocess_timeout_seconds: int = 300

    max_upload_size_mb: int = 50
    max_audio_duration_seconds: int = 120
    max_video_duration_seconds: int = 300

    rvc_device: str = "cuda:0"
    rvc_backend: str = "passthrough"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
