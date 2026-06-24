from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings
from app.media.ffmpeg import convert_audio, normalize_audio, probe_media, run_media_command


def run() -> None:
    settings = get_settings()
    smoke_dir = Path(settings.storage_root) / "tmp" / "media-smoke"
    smoke_dir.mkdir(parents=True, exist_ok=True)

    source = smoke_dir / "source.wav"
    normalized = smoke_dir / "normalized.wav"
    converted = smoke_dir / "converted.mp3"

    run_media_command(
        [
            settings.ffmpeg_binary,
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=1000:duration=1",
            str(source),
        ]
    )
    normalize_audio(source, normalized)
    convert_audio(normalized, converted, codec="libmp3lame")

    probe = probe_media(converted)
    if probe.duration_seconds is None or probe.duration_seconds <= 0:
        raise SystemExit("media smoke failed: duration was not detected")

    print(f"media smoke ok: {converted} duration={probe.duration_seconds:.3f}")
