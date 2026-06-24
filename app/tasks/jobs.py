from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from app.core.config import get_settings
from app.db.enums import TaskStage, TaskStatus
from app.db.session import async_session_factory
from app.tasks.progress import set_task_progress


def run_demo_task_progress(task_id: str, duration_seconds: float = 1.0) -> dict[str, str | int]:
    return asyncio.run(_run_demo_task_progress(task_id, duration_seconds))


async def _run_demo_task_progress(task_id: str, duration_seconds: float) -> dict[str, str | int]:
    sleep_seconds = max(0.05, duration_seconds / 4)
    updates = [
        (TaskStatus.RUNNING, TaskStage.PREPROCESSING, 20, "Task preprocessing started"),
        (TaskStatus.RUNNING, TaskStage.CONVERTING_VOICE, 55, "Voice conversion started"),
        (TaskStatus.RUNNING, TaskStage.UPLOADING_RESULT, 85, "Preparing task result"),
    ]

    for status, stage, progress, message in updates:
        async with async_session_factory() as session:
            await set_task_progress(
                session,
                task_id,
                status=status,
                stage=stage,
                progress=progress,
                log_message=message,
            )
        time.sleep(sleep_seconds)

    settings = get_settings()
    output_dir = Path(settings.storage_root) / "outputs" / "tasks"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{task_id}.json"
    output_path.write_text(
        json.dumps({"task_id": task_id, "status": "completed"}, indent=2),
        encoding="utf-8",
    )

    async with async_session_factory() as session:
        await set_task_progress(
            session,
            task_id,
            status=TaskStatus.COMPLETED,
            stage=TaskStage.DONE,
            progress=100,
            output_file_path=str(output_path),
            log_message="Task completed",
        )

    return {"task_id": task_id, "status": "completed", "progress": 100}
