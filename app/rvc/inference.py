from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.config import get_settings
from app.media.ffmpeg import convert_audio, probe_media
from app.rvc.registry import resolve_model_file


class RvcInferenceError(RuntimeError):
    pass


@dataclass(frozen=True)
class RvcInferenceRequest:
    input_audio_path: Path
    model_path: str
    output_audio_path: Path
    index_path: str | None = None
    pitch_shift: int = 0


@dataclass(frozen=True)
class RvcInferenceResult:
    output_audio_path: Path
    duration_seconds: float | None
    backend: str


class RvcInferenceService:
    def __init__(self, backend: str | None = None, models_root: Path | None = None) -> None:
        settings = get_settings()
        self._backend = backend or settings.rvc_backend
        self._models_root = models_root or settings.models_root

    def convert_voice(self, request: RvcInferenceRequest) -> RvcInferenceResult:
        if not request.input_audio_path.exists():
            raise RvcInferenceError(f"input audio does not exist: {request.input_audio_path}")

        resolve_model_file(self._models_root, request.model_path, required_suffix=".pth")
        if request.index_path is not None:
            resolve_model_file(self._models_root, request.index_path)

        if self._backend != "passthrough":
            raise RvcInferenceError(f"unsupported RVC backend: {self._backend}")

        output_path = convert_audio(request.input_audio_path, request.output_audio_path)
        probe = probe_media(output_path)

        return RvcInferenceResult(
            output_audio_path=output_path,
            duration_seconds=probe.duration_seconds,
            backend=self._backend,
        )
