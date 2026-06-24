from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_settings_dependency
from app.core.config import Settings
from app.db.enums import TaskStage, TaskStatus, TaskType
from app.db.models import Task, TaskLog, User
from app.db.session import get_session
from app.gemini.jobs import run_gemini_transcription_task
from app.storage.paths import StoragePathError, resolve_storage_file
from app.tasks.jobs import run_demo_task_progress
from app.workers.queue import create_queue

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskCreateRequest(BaseModel):
    telegram_user_id: int
    telegram_file_id: str
    media_kind: str
    mime_type: str | None = None
    file_name: str | None = None
    size_bytes: int | None = None
    duration_seconds: int | None = None


class TranscriptionTaskCreateRequest(BaseModel):
    telegram_user_id: int = Field(default=0)
    input_file_path: str
    mime_type: str = "audio/wav"


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str
    status: str
    progress: int
    stage: str
    input_file_path: str | None
    output_file_path: str | None
    error_message: str | None
    parameters: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class TaskResultResponse(BaseModel):
    id: uuid.UUID
    status: str
    progress: int
    stage: str
    output_file_path: str | None
    error_message: str | None
    parameters: dict[str, Any]


class TaskLogResponse(BaseModel):
    created_at: datetime
    level: str
    message: str
    context: dict[str, Any]


async def _get_or_create_user(session: AsyncSession, telegram_user_id: int) -> User:
    result = await session.execute(select(User).where(User.telegram_id == telegram_user_id))
    user = result.scalar_one_or_none()
    if user is not None:
        return user

    user = User(telegram_id=telegram_user_id)
    session.add(user)
    await session.flush()
    return user


async def _get_task_or_404(session: AsyncSession, task_id: uuid.UUID) -> Task:
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreateRequest,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings_dependency),
) -> Task:
    user = await _get_or_create_user(session, payload.telegram_user_id)
    task = Task(
        user_id=user.id,
        type=TaskType.VOICE_CONVERSION,
        status=TaskStatus.QUEUED,
        progress=5,
        stage=TaskStage.QUEUED,
        parameters=payload.model_dump(),
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    queue = create_queue(settings.redis_url)
    queue.enqueue(run_demo_task_progress, str(task.id), job_timeout=120)
    return task


@router.post("/transcriptions", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_transcription_task(
    payload: TranscriptionTaskCreateRequest,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings_dependency),
) -> Task:
    try:
        resolve_storage_file(settings.storage_root, payload.input_file_path)
    except StoragePathError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    user = await _get_or_create_user(session, payload.telegram_user_id)
    task = Task(
        user_id=user.id,
        type=TaskType.TRANSCRIPTION,
        status=TaskStatus.QUEUED,
        progress=5,
        stage=TaskStage.QUEUED,
        input_file_path=payload.input_file_path,
        parameters={"mime_type": payload.mime_type},
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    queue = create_queue(settings.redis_url)
    queue.enqueue(
        run_gemini_transcription_task,
        str(task.id),
        payload.input_file_path,
        payload.mime_type,
        job_timeout=settings.gemini_timeout_seconds + 60,
    )
    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> Task:
    return await _get_task_or_404(session, task_id)


@router.get("/{task_id}/result", response_model=TaskResultResponse)
async def get_task_result(task_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> TaskResultResponse:
    task = await _get_task_or_404(session, task_id)
    return TaskResultResponse(
        id=task.id,
        status=task.status,
        progress=task.progress,
        stage=task.stage,
        output_file_path=task.output_file_path,
        error_message=task.error_message,
        parameters=task.parameters,
    )


@router.get("/{task_id}/logs", response_model=list[TaskLogResponse])
async def get_task_logs(task_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> list[TaskLogResponse]:
    await _get_task_or_404(session, task_id)
    result = await session.execute(
        select(TaskLog).where(TaskLog.task_id == task_id).order_by(TaskLog.created_at.asc())
    )
    return [TaskLogResponse.model_validate(log, from_attributes=True) for log in result.scalars()]
