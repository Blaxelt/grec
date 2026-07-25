from typing import Annotated, Literal

from pydantic import Field, model_validator
from sqlmodel import SQLModel

from app.models import GameRecommendation


class ChatMessage(SQLModel):
    """A single message in the conversation history (kept client-side)."""

    role: Literal["user", "assistant"]
    content: Annotated[str, Field(min_length=1, max_length=4000)]


class ChatRequest(SQLModel):
    """Request body for the /chat endpoint."""

    message: Annotated[str, Field(min_length=1, max_length=4000)]
    history: Annotated[list[ChatMessage], Field(max_length=20)] = []
    app_ids: Annotated[list[int] | None, Field(max_length=1000)] = None
    hours_played: Annotated[list[Annotated[float, Field(ge=0)]] | None, Field(max_length=1000)] = None

    @model_validator(mode="after")
    def check_library_lengths(self):
        if (self.app_ids is None) != (self.hours_played is None):
            raise ValueError("app_ids and hours_played must be provided together")
        if self.app_ids is not None and len(self.app_ids) != len(self.hours_played):
            raise ValueError("app_ids and hours_played must have the same length")
        return self

    @property
    def has_library(self) -> bool:
        return bool(self.app_ids)


class ChatResponse(SQLModel):
    """Response wrapper for the /chat endpoint."""

    reply: str
    games: list[GameRecommendation]
