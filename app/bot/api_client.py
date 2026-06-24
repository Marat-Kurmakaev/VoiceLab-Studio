from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IncomingMedia:
    telegram_user_id: int
    telegram_file_id: str
    media_kind: str
    mime_type: str | None = None
    file_name: str | None = None
    size_bytes: int | None = None
    duration_seconds: int | None = None


class ApiClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def create_voice_conversion_task(self, media: IncomingMedia) -> str | None:
        payload = {
            "telegram_user_id": media.telegram_user_id,
            "telegram_file_id": media.telegram_file_id,
            "media_kind": media.media_kind,
            "mime_type": media.mime_type,
            "file_name": media.file_name,
            "size_bytes": media.size_bytes,
            "duration_seconds": media.duration_seconds,
        }

        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=10) as client:
                response = await client.post("/tasks", json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Task creation API is not available yet: %s", exc)
            return None

        data = response.json()
        task_id = data.get("id")
        return str(task_id) if task_id else None
