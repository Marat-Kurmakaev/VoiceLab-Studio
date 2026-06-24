from __future__ import annotations

from pathlib import Path

from app.rvc.inference import RvcInferenceRequest, RvcInferenceService


def run_rvc_voice_conversion(
    input_audio_path: str,
    model_path: str,
    output_audio_path: str,
    index_path: str | None = None,
    pitch_shift: int = 0,
) -> dict[str, str | float | None]:
    result = RvcInferenceService().convert_voice(
        RvcInferenceRequest(
            input_audio_path=Path(input_audio_path),
            model_path=model_path,
            output_audio_path=Path(output_audio_path),
            index_path=index_path,
            pitch_shift=pitch_shift,
        )
    )

    return {
        "output_audio_path": str(result.output_audio_path),
        "duration_seconds": result.duration_seconds,
        "backend": result.backend,
    }
