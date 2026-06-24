from __future__ import annotations

from app.core.config import Settings, get_settings
from app.db.session import get_session


def get_settings_dependency() -> Settings:
    return get_settings()


__all__ = ["get_session", "get_settings_dependency"]
