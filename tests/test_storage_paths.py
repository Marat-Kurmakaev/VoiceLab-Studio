from pathlib import Path

import pytest

from app.storage.paths import StoragePathError, resolve_storage_file


def test_resolve_storage_file_rejects_escape(tmp_path: Path) -> None:
    storage = tmp_path / "storage"
    storage.mkdir()

    with pytest.raises(StoragePathError):
        resolve_storage_file(storage, "../secret.wav")


def test_resolve_storage_file_returns_file_inside_storage(tmp_path: Path) -> None:
    storage = tmp_path / "storage"
    source = storage / "uploads" / "input.wav"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"audio")

    assert resolve_storage_file(storage, "uploads/input.wav") == source.resolve()
