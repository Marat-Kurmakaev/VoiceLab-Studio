from __future__ import annotations

import asyncio
from pathlib import Path

from app.core.config import get_settings
from app.db.enums import TaskStage, TaskStatus
from app.db.session import async_session_factory
from app.gemini.transcription import (
    GeminiTranscriptionError,
    GeminiTranscriptionRequest,
    GeminiTranscriptionService,
)
from app.storage.paths import resolve_storage_file
from app.tasks.progress import set_task_progress


def run_gemini_transcription_task(task_id: str, input_file_path: str, mime_type: str) -> dict[str, str | int]:
    return asyncio.run(_run_gemini_transcription_task(task_id, input_file_path, mime_type))


async def _run_gemini_transcription_task(task_id: str, input_file_path: str, mime_type: str) -> dict[str, str | int]:
    settings = get_settings()
    try:
        async with async_session_factory() as session:
            await set_task_progress(
                session,
                task_id,
                status=TaskStatus.RUNNING,
                stage=TaskStage.TRANSCRIBING,
                progress=20,
                log_message="Gemini transcription started",
            )

        source_path = resolve_storage_file(Path(settings.storage_root), input_file_path)
        result = await GeminiTranscriptionService(settings=settings).transcribe(
            GeminiTranscriptionRequest(input_file_path=source_path, mime_type=mime_type)
        )

        output_dir = Path(settings.storage_root) / "outputs" / "transcripts"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{task_id}.txt"
        output_path.write_text(result.transcript, encoding="utf-8")

        async with async_session_factory() as session:
            await set_task_progress(
                session,
                task_id,
                status=TaskStatus.COMPLETED,
                stage=TaskStage.DONE,
                progress=100,
                output_file_path=str(output_path),
                parameters_update={
                    "transcript_backend": result.backend,
                    "transcript_model": result.model,
                },
                log_message="Gemini transcription completed",
            )
    except (GeminiTranscriptionError, OSError, ValueError) as exc:
        async with async_session_factory() as session:
            await set_task_progress(
                session,
                task_id,
                status=TaskStatus.FAILED,
                stage=TaskStage.TRANSCRIBING,
                progress=100,
                error_message=str(exc),
                log_message="Gemini transcription failed",
            )
        raise

    return {"task_id": task_id, "status": "completed", "progress": 100, "output_file_path": str(output_path)}
