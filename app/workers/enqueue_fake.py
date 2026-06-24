from __future__ import annotations

from uuid import uuid4

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.workers.jobs import run_fake_voice_conversion
from app.workers.queue import create_queue


def run() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    queue = create_queue(settings.redis_url)
    task_id = str(uuid4())
    job = queue.enqueue(run_fake_voice_conversion, task_id, job_timeout=60)
    print(f"{job.id} {task_id}")
