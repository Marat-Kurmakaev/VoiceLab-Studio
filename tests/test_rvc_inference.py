from pathlib import Path

from app.rvc.inference import RvcInferenceRequest, RvcInferenceService


def test_passthrough_backend_validates_model_and_writes_output(monkeypatch, tmp_path: Path) -> None:
    model = tmp_path / "models" / "voice.pth"
    model.parent.mkdir()
    model.write_bytes(b"model")
    input_audio = tmp_path / "input.wav"
    input_audio.write_bytes(b"audio")
    output_audio = tmp_path / "output.wav"

    monkeypatch.setattr(
        "app.rvc.inference.convert_audio",
        lambda source, target: target.write_bytes(b"converted") or target,
    )
    monkeypatch.setattr(
        "app.rvc.inference.probe_media",
        lambda path: type("Probe", (), {"duration_seconds": 1.0})(),
    )

    result = RvcInferenceService(backend="passthrough", models_root=model.parent).convert_voice(
        RvcInferenceRequest(
            input_audio_path=input_audio,
            model_path="voice.pth",
            output_audio_path=output_audio,
        )
    )

    assert result.output_audio_path == output_audio
    assert result.duration_seconds == 1.0
    assert result.backend == "passthrough"
