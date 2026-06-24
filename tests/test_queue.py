from app.workers.queue import DEFAULT_QUEUE_NAME


def test_default_queue_name_is_stable() -> None:
    assert DEFAULT_QUEUE_NAME == "voicelab"
