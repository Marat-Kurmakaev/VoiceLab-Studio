from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.api_client import ApiClient, IncomingMedia
from app.bot.keyboards import main_menu

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        "VoiceLab Studio is ready. Send a voice message, audio, or video to create a processing task.",
        reply_markup=main_menu(),
    )


@router.message(F.text.casefold() == "help")
async def handle_help(message: Message) -> None:
    await message.answer(
        "Send voice, audio, or video. The bot will create a task through the API and show its status when the API is enabled.",
        reply_markup=main_menu(),
    )


@router.message(F.text.casefold() == "task status")
async def handle_status_placeholder(message: Message) -> None:
    await message.answer("Task status lookup will be connected after the API task endpoints are implemented.")


@router.message(F.voice)
async def handle_voice(message: Message, api_client: ApiClient) -> None:
    voice = message.voice
    if voice is None or message.from_user is None:
        return

    await create_task(
        message,
        api_client,
        IncomingMedia(
            telegram_user_id=message.from_user.id,
            telegram_file_id=voice.file_id,
            media_kind="voice",
            mime_type=voice.mime_type,
            size_bytes=voice.file_size,
            duration_seconds=voice.duration,
        ),
    )


@router.message(F.audio)
async def handle_audio(message: Message, api_client: ApiClient) -> None:
    audio = message.audio
    if audio is None or message.from_user is None:
        return

    await create_task(
        message,
        api_client,
        IncomingMedia(
            telegram_user_id=message.from_user.id,
            telegram_file_id=audio.file_id,
            media_kind="audio",
            mime_type=audio.mime_type,
            file_name=audio.file_name,
            size_bytes=audio.file_size,
            duration_seconds=audio.duration,
        ),
    )


@router.message(F.video)
async def handle_video(message: Message, api_client: ApiClient) -> None:
    video = message.video
    if video is None or message.from_user is None:
        return

    await create_task(
        message,
        api_client,
        IncomingMedia(
            telegram_user_id=message.from_user.id,
            telegram_file_id=video.file_id,
            media_kind="video",
            mime_type=video.mime_type,
            file_name=video.file_name,
            size_bytes=video.file_size,
            duration_seconds=video.duration,
        ),
    )


async def create_task(message: Message, api_client: ApiClient, media: IncomingMedia) -> None:
    task_id = await api_client.create_voice_conversion_task(media)

    if task_id is None:
        await message.answer("File received. Task API is not connected yet, so processing was not queued.")
        return

    await message.answer(f"Task created: {task_id}")
