from app.db.base import Base
from app.db import models  # noqa: F401


def test_expected_tables_are_registered() -> None:
    assert {
        "users",
        "voice_models",
        "tasks",
        "stored_files",
        "task_logs",
    }.issubset(Base.metadata.tables)
