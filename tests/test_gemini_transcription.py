from pathlib import Path
import asyncio

from app.core.config import Settings
from app.gemini.transcription import GeminiTranscriptionRequest, GeminiTranscriptionService


def test_mock_gemini_transcription_returns_text(tmp_path: Path) -> None:
    source = tmp_path / "input.wav"
    source.write_bytes(b"audio")
    settings = Settings(gemini_api_key="replace-me", gemini_transcription_backend="auto")

    result = asyncio.run(
        GeminiTranscriptionService(settings=settings).transcribe(
            GeminiTranscriptionRequest(input_file_path=source, mime_type="audio/wav")
        )
    )

    assert result.backend == "mock"
    assert "input.wav" in result.transcript
