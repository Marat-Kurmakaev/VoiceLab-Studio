from __future__ import annotations

from pathlib import Path


class StoragePathError(ValueError):
    pass


def resolve_storage_file(
    storage_root: Path,
    relative_path: str,
    *,
    required_suffixes: set[str] | None = None,
) -> Path:
    requested = Path(relative_path)
    if requested.is_absolute() or ".." in requested.parts:
        raise StoragePathError("Storage path must be relative and stay inside storage root.")

    root = storage_root.resolve()
    resolved = (root / requested).resolve()
    if root != resolved and root not in resolved.parents:
        raise StoragePathError("Storage path escapes storage root.")

    if required_suffixes and resolved.suffix.lower() not in required_suffixes:
        raise StoragePathError(f"Storage file must have one of these suffixes: {sorted(required_suffixes)}.")

    if not resolved.is_file():
        raise StoragePathError("Storage file does not exist.")

    return resolved
