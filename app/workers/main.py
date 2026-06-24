from __future__ import annotations

import logging

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.workers.queue import create_worker

logger = logging.getLogger(__name__)


def run() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    worker = create_worker(settings.redis_url)
    logger.info("RQ worker started")
    worker.work(with_scheduler=False)
