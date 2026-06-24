from __future__ import annotations

import asyncio
import logging
import time

from aiogram import Bot, Dispatcher

from app.bot.api_client import ApiClient
from app.bot.handlers import router
from app.core.config import get_settings
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    if settings.telegram_bot_token == "replace-me":
        logger.warning("TELEGRAM_BOT_TOKEN is not configured; bot placeholder started")
        await sleep_forever()
        return

    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = Dispatcher(api_client=ApiClient(settings.api_base_url))
    dispatcher.include_router(router)

    logger.info("Telegram bot polling started")
    await dispatcher.start_polling(bot)


async def sleep_forever() -> None:
    while True:
        await asyncio.sleep(60)


def run() -> None:
    asyncio.run(main())


def run_placeholder() -> None:
    logger.info("Telegram bot placeholder started")
    while True:
        time.sleep(60)
