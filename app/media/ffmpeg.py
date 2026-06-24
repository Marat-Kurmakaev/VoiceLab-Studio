from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class MediaCommandError(RuntimeError):
    def __init__(self, command: Sequence[str], returncode: int, stderr: str) -> None:
        self.command = list(command)
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f"Media command failed with code {returncode}: {' '.join(command)}")


@dataclass(frozen=True)
class MediaProbe:
    duration_seconds: float | None
    format_name: str | None


def run_media_command(command: Sequence[str], timeout_seconds: int | None = None) -> subprocess.CompletedProcess[str]:
    settings = get_settings()
    timeout = timeout_seconds or settings.media_subprocess_timeout_seconds
    logger.info("Running media command: %s", " ".join(command))

    completed = subprocess.run(
        list(command),
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if completed.returncode != 0:
        logger.warning("Media command failed: %s", completed.stderr.strip())
        raise MediaCommandError(command, completed.returncode, completed.stderr)

    return completed


def probe_media(input_path: Path) -> MediaProbe:
    settings = get_settings()
    completed = run_media_command(
        [
            settings.ffprobe_binary,
            "-v",
            "error",
            "-show_entries",
            "format=duration,format_name",
            "-of",
            "json",
            str(input_path),
        ]
    )
    data = json.loads(completed.stdout)
    media_format = data.get("format", {})
    duration = media_format.get("duration")

    return MediaProbe(
        duration_seconds=float(duration) if duration is not None else None,
        format_name=media_format.get("format_name"),
    )


def extract_audio(input_video: Path, output_audio: Path, sample_rate: int = 44100) -> Path:
    output_audio.parent.mkdir(parents=True, exist_ok=True)
    settings = get_settings()
    run_media_command(
        [
            settings.ffmpeg_binary,
            "-y",
            "-i",
            str(input_video),
            "-vn",
            "-ac",
            "2",
            "-ar",
            str(sample_rate),
            str(output_audio),
        ]
    )
    return output_audio


def normalize_audio(input_audio: Path, output_audio: Path) -> Path:
    output_audio.parent.mkdir(parents=True, exist_ok=True)
    settings = get_settings()
    run_media_command(
        [
            settings.ffmpeg_binary,
            "-y",
            "-i",
            str(input_audio),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11",
            str(output_audio),
        ]
    )
    return output_audio


def convert_audio(input_audio: Path, output_audio: Path, codec: str = "pcm_s16le") -> Path:
    output_audio.parent.mkdir(parents=True, exist_ok=True)
    settings = get_settings()
    run_media_command(
        [
            settings.ffmpeg_binary,
            "-y",
            "-i",
            str(input_audio),
            "-acodec",
            codec,
            str(output_audio),
        ]
    )
    return output_audio


def replace_video_audio(input_video: Path, input_audio: Path, output_video: Path) -> Path:
    output_video.parent.mkdir(parents=True, exist_ok=True)
    settings = get_settings()
    run_media_command(
        [
            settings.ffmpeg_binary,
            "-y",
            "-i",
            str(input_video),
            "-i",
            str(input_audio),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-shortest",
            str(output_video),
        ]
    )
    return output_video
