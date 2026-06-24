from pathlib import Path

import pytest

from app.rvc.registry import ModelPathError, resolve_model_file


def test_resolve_model_file_accepts_file_under_models_root(tmp_path: Path) -> None:
    model = tmp_path / "voice" / "model.pth"
    model.parent.mkdir()
    model.write_bytes(b"model")

    assert resolve_model_file(tmp_path, "voice/model.pth", required_suffix=".pth") == model.resolve()


@pytest.mark.parametrize("path", ["../model.pth", "/tmp/model.pth", "voice/model.index"])
def test_resolve_model_file_rejects_unsafe_or_wrong_paths(tmp_path: Path, path: str) -> None:
    with pytest.raises(ModelPathError):
        resolve_model_file(tmp_path, path, required_suffix=".pth")
