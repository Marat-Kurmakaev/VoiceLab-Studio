from __future__ import annotations

import json
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def run_fake_voice_conversion(task_id: str | None = None, duration_seconds: float = 0.1) -> dict[str, str]:
    task_id = task_id or str(uuid4())
    settings = get_settings()
    output_dir = Path(settings.storage_root) / "tmp" / "queue"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Fake voice conversion started: task_id=%s", task_id)
    time.sleep(duration_seconds)

    result = {
        "task_id": task_id,
        "status": "completed",
        "finished_at": datetime.now(UTC).isoformat(),
    }
    result_path = output_dir / f"{task_id}.json"
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    logger.info("Fake voice conversion completed: task_id=%s", task_id)

    return result
