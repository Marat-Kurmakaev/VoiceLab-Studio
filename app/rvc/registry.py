from __future__ import annotations

from pathlib import Path


class ModelPathError(ValueError):
    pass


def resolve_model_file(models_root: Path, relative_path: str, required_suffix: str | None = None) -> Path:
    raw_path = Path(relative_path)
    if raw_path.is_absolute():
        raise ModelPathError("model paths must be relative to MODELS_ROOT")
    if any(part == ".." for part in raw_path.parts):
        raise ModelPathError("model paths cannot contain '..'")
    if required_suffix is not None and raw_path.suffix.lower() != required_suffix:
        raise ModelPathError(f"model path must end with {required_suffix}")

    root = models_root.resolve()
    resolved = (root / raw_path).resolve()

    if root != resolved and root not in resolved.parents:
        raise ModelPathError("model path escapes MODELS_ROOT")
    if not resolved.exists():
        raise ModelPathError(f"model file does not exist: {relative_path}")
    if not resolved.is_file():
        raise ModelPathError(f"model path is not a file: {relative_path}")

    return resolved
