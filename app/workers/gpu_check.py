from __future__ import annotations

import logging

from app.core.config import get_settings
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    try:
        import torch
    except ImportError as exc:
        raise SystemExit("PyTorch is not installed in this image") from exc

    is_available = torch.cuda.is_available()
    logger.info("torch.cuda.is_available() == %s", is_available)

    if not is_available:
        raise SystemExit("CUDA is not available inside the container")

    logger.info("CUDA device: %s", torch.cuda.get_device_name(0))


if __name__ == "__main__":
    main()
