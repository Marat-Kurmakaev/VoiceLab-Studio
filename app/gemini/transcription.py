from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

import httpx

from app.core.config import Settings, get_settings


class GeminiTranscriptionError(RuntimeError):
    pass


@dataclass(frozen=True)
class GeminiTranscriptionRequest:
    input_file_path: Path
    mime_type: str
    prompt: str = "Generate a plain text transcript of the speech in this audio. Return only the transcript."


@dataclass(frozen=True)
class GeminiTranscriptionResult:
    transcript: str
    backend: str
    model: str


class GeminiTranscriptionService:
    def __init__(
        self,
        *,
        settings: Settings | None = None,
        backend: str | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._backend = (backend or self._settings.gemini_transcription_backend).lower()

    async def transcribe(self, request: GeminiTranscriptionRequest) -> GeminiTranscriptionResult:
        if not request.input_file_path.is_file():
            raise GeminiTranscriptionError(f"Input media does not exist: {request.input_file_path}")

        backend = self._resolve_backend()
        if backend == "mock":
            return GeminiTranscriptionResult(
                transcript=f"Mock transcript for {request.input_file_path.name}.",
                backend="mock",
                model=self._settings.gemini_model,
            )
        if backend != "api":
            raise GeminiTranscriptionError(f"Unsupported Gemini transcription backend: {self._backend}")

        transcript = await self._transcribe_with_api(request)
        return GeminiTranscriptionResult(transcript=transcript, backend="api", model=self._settings.gemini_model)

    def _resolve_backend(self) -> str:
        if self._backend != "auto":
            return self._backend
        return "api" if self._settings.gemini_api_key and self._settings.gemini_api_key != "replace-me" else "mock"

    async def _transcribe_with_api(self, request: GeminiTranscriptionRequest) -> str:
        max_bytes = self._settings.gemini_max_inline_mb * 1024 * 1024
        audio_bytes = request.input_file_path.read_bytes()
        if len(audio_bytes) > max_bytes:
            raise GeminiTranscriptionError(
                f"Inline Gemini transcription is limited to {self._settings.gemini_max_inline_mb} MB."
            )

        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._settings.gemini_model}:generateContent"
        )
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": request.prompt},
                        {
                            "inline_data": {
                                "mime_type": request.mime_type,
                                "data": base64.b64encode(audio_bytes).decode("ascii"),
                            }
                        },
                    ]
                }
            ]
        }

        async with httpx.AsyncClient(timeout=self._settings.gemini_timeout_seconds) as client:
            response = await client.post(endpoint, params={"key": self._settings.gemini_api_key}, json=payload)

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise GeminiTranscriptionError(f"Gemini API request failed: HTTP {exc.response.status_code}") from exc

        data = response.json()
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        transcript = "\n".join(part.get("text", "") for part in parts).strip()
        if not transcript:
            raise GeminiTranscriptionError("Gemini API returned an empty transcript.")
        return transcript
