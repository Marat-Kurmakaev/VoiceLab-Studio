from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Voice conversion")],
            [KeyboardButton(text="Task status"), KeyboardButton(text="Help")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Send voice, audio, or video",
    )
