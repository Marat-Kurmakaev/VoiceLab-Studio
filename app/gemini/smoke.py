from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings
from app.gemini.transcription import GeminiTranscriptionRequest, GeminiTranscriptionService


async def _run_async() -> None:
    settings = get_settings()
    smoke_dir = Path(settings.storage_root) / "tmp" / "gemini-smoke"
    smoke_dir.mkdir(parents=True, exist_ok=True)
    input_file = smoke_dir / "input.txt"
    input_file.write_text("local smoke payload", encoding="utf-8")

    result = await GeminiTranscriptionService(settings=settings, backend="mock").transcribe(
        GeminiTranscriptionRequest(input_file_path=input_file, mime_type="text/plain")
    )
    print(f"gemini smoke ok: backend={result.backend} model={result.model}")


def run() -> None:
    import asyncio

    asyncio.run(_run_async())
