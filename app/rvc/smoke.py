from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings
from app.media.ffmpeg import run_media_command
from app.rvc.inference import RvcInferenceRequest, RvcInferenceService


def run() -> None:
    settings = get_settings()
    smoke_dir = Path(settings.storage_root) / "tmp" / "rvc-smoke"
    input_audio = smoke_dir / "input.wav"
    output_audio = smoke_dir / "output.wav"
    model_dir = Path(settings.models_root) / "smoke"
    model_path = model_dir / "voice.pth"

    smoke_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path.write_bytes(b"placeholder model for headless RVC smoke test\n")

    run_media_command(
        [
            settings.ffmpeg_binary,
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=1",
            str(input_audio),
        ]
    )

    result = RvcInferenceService().convert_voice(
        RvcInferenceRequest(
            input_audio_path=input_audio,
            model_path="smoke/voice.pth",
            output_audio_path=output_audio,
        )
    )

    if result.duration_seconds is None or result.duration_seconds <= 0:
        raise SystemExit("rvc smoke failed: output duration was not detected")

    print(
        f"rvc smoke ok: {result.output_audio_path} "
        f"duration={result.duration_seconds:.3f} backend={result.backend}"
    )
