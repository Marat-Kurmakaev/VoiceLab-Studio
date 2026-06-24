from app.tasks.progress import clamp_progress


def test_clamp_progress() -> None:
    assert clamp_progress(-1) == 0
    assert clamp_progress(50) == 50
    assert clamp_progress(101) == 100
