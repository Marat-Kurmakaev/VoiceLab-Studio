from __future__ import annotations

from redis import Redis
from rq import Queue, Worker

DEFAULT_QUEUE_NAME = "voicelab"


def create_redis_connection(redis_url: str) -> Redis:
    return Redis.from_url(redis_url)


def create_queue(redis_url: str, name: str = DEFAULT_QUEUE_NAME) -> Queue:
    return Queue(name=name, connection=create_redis_connection(redis_url))


def create_worker(redis_url: str, name: str = DEFAULT_QUEUE_NAME) -> Worker:
    connection = create_redis_connection(redis_url)
    queue = Queue(name=name, connection=connection)
    return Worker([queue], connection=connection)
