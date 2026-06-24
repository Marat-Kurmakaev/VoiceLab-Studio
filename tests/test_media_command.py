from pathlib import Path
from subprocess import CompletedProcess

from app.media import ffmpeg


def test_run_media_command_uses_argument_list(monkeypatch) -> None:
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(ffmpeg.subprocess, "run", fake_run)

    ffmpeg.run_media_command(["ffmpeg", "-version"])

    command, kwargs = calls[0]
    assert command == ["ffmpeg", "-version"]
    assert kwargs["check"] is False
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True


def test_extract_audio_creates_output_parent(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        ffmpeg,
        "run_media_command",
        lambda command: CompletedProcess(command, 0, stdout="", stderr=""),
    )

    output = tmp_path / "nested" / "audio.wav"
    ffmpeg.extract_audio(tmp_path / "input.mp4", output)

    assert output.parent.exists()
