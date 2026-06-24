from __future__ import annotations

from enum import StrEnum


class TaskStatus(StrEnum):
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStage(StrEnum):
    UPLOADED = "uploaded"
    QUEUED = "queued"
    PREPROCESSING = "preprocessing"
    TRANSCRIBING = "transcribing"
    TRANSLATING = "translating"
    CONVERTING_VOICE = "converting_voice"
    ASSEMBLING = "assembling"
    UPLOADING_RESULT = "uploading_result"
    DONE = "done"


class TaskType(StrEnum):
    TRANSCRIPTION = "transcription"
    VOICE_CONVERSION = "voice_conversion"
    AUDIO_COVER = "audio_cover"
    VIDEO_EXTRACT_AUDIO = "video_extract_audio"
    VIDEO_SUBTITLES = "video_subtitles"
    VIDEO_TRANSLATION = "video_translation"
    VIDEO_DUBBING = "video_dubbing"


class FileKind(StrEnum):
    INPUT = "input"
    OUTPUT = "output"
    TEMP = "temp"
    MODEL = "model"
