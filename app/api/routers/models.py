from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.core.config import get_settings
from app.db.models import VoiceModel
from app.rvc.registry import ModelPathError, resolve_model_file

router = APIRouter(prefix="/models", tags=["models"])


class VoiceModelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None
    model_path: str = Field(min_length=1, max_length=1024)
    index_path: str | None = Field(default=None, max_length=1024)
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class VoiceModelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    model_path: str
    index_path: str | None
    metadata_json: dict


@router.get("", response_model=list[VoiceModelRead])
async def list_models(session: Annotated[AsyncSession, Depends(get_session)]) -> list[VoiceModel]:
    result = await session.scalars(select(VoiceModel).order_by(VoiceModel.name))
    return list(result)


@router.post("", response_model=VoiceModelRead, status_code=status.HTTP_201_CREATED)
async def add_model(
    payload: VoiceModelCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> VoiceModel:
    settings = get_settings()
    try:
        resolve_model_file(settings.models_root, payload.model_path, required_suffix=".pth")
        if payload.index_path is not None:
            resolve_model_file(settings.models_root, payload.index_path)
    except ModelPathError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    model = VoiceModel(
        name=payload.name,
        description=payload.description,
        model_path=payload.model_path,
        index_path=payload.index_path,
        metadata_json=dict(payload.metadata),
    )
    session.add(model)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="model name already exists") from exc

    await session.refresh(model)
    return model


@router.get("/{model_id}", response_model=VoiceModelRead)
async def get_model(
    model_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> VoiceModel:
    model = await session.get(VoiceModel, model_id)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="model not found")
    return model
