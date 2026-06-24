from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import TaskStage, TaskStatus
from app.db.models import Task, TaskLog


class TaskProgressError(RuntimeError):
    pass


@dataclass(frozen=True)
class TaskProgressSnapshot:
    task_id: uuid.UUID
    status: TaskStatus
    stage: TaskStage
    progress: int
    output_file_path: str | None
    error_message: str | None


def clamp_progress(progress: int) -> int:
    return max(0, min(100, progress))


async def set_task_progress(
    session: AsyncSession,
    task_id: str | uuid.UUID,
    *,
    status: TaskStatus | None = None,
    stage: TaskStage | None = None,
    progress: int | None = None,
    output_file_path: str | None = None,
    error_message: str | None = None,
    parameters_update: dict[str, Any] | None = None,
    log_message: str | None = None,
) -> TaskProgressSnapshot:
    task_uuid = uuid.UUID(str(task_id))
    task = await session.get(Task, task_uuid)
    if task is None:
        raise TaskProgressError(f"Task not found: {task_uuid}")

    now = datetime.now(UTC)
    if status is not None:
        task.status = status
        if status == TaskStatus.RUNNING and task.started_at is None:
            task.started_at = now
        if status in {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}:
            task.finished_at = now
    if stage is not None:
        task.stage = stage
    if progress is not None:
        task.progress = clamp_progress(progress)
    if output_file_path is not None:
        task.output_file_path = output_file_path
    if error_message is not None:
        task.error_message = error_message
    if parameters_update:
        parameters = dict(task.parameters or {})
        parameters.update(parameters_update)
        task.parameters = parameters

    session.add(
        TaskLog(
            task_id=task.id,
            level="info" if status != TaskStatus.FAILED else "error",
            message=log_message or f"Task progress updated: {task.progress}%",
            context={
                "status": task.status,
                "stage": task.stage,
                "progress": task.progress,
            },
        )
    )
    await session.commit()
    await session.refresh(task)

    return TaskProgressSnapshot(
        task_id=task.id,
        status=TaskStatus(task.status),
        stage=TaskStage(task.stage),
        progress=task.progress,
        output_file_path=task.output_file_path,
        error_message=task.error_message,
    )
