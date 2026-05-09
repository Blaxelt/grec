from typing import Annotated

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, SQLModel
from pydantic import model_validator

class Game(SQLModel, table=True):
    """Maps to the existing 'games' table created by the pipeline."""

    __tablename__ = "games"

    app_id: int = Field(primary_key=True)
    game_name: str
    header_image: str | None
    short_description: str
    genres: list[str] = Field(sa_column=Column(ARRAY(Text)))
    tags: list[str] = Field(sa_column=Column(ARRAY(Text)))
    screenshots: list[str] | None = Field(default=None, sa_column=Column(ARRAY(Text)))
    combined_vector: list[float] = Field(sa_column=Column(Vector()))
    wilson_score: float 

class GameSearchResult(SQLModel):
    """Search result."""

    app_id: int
    game_name: str

class PlayedGameResponse(SQLModel):
    """A game played by a user fetched from Steam."""

    app_id: int
    game_name: str
    hours: float

class GameRecommendation(SQLModel):
    """A single recommended game."""

    app_id: int
    game_name: str
    header_image: str | None
    hybrid_score: float

class GameDetail(SQLModel):
    """Full game detail for /games/{app_id}."""

    app_id: int
    game_name: str
    header_image: str | None
    short_description: str
    genres: list[str]
    tags: list[str]
    screenshots: list[str] | None
    wilson_score: float
    other_players_also_played: list[GameRecommendation] | None

class RecommendationResponse(SQLModel):
    """Response wrapper for the /recommend endpoint."""

    target_game: str
    recommendations: list[GameRecommendation]

class ProfileRequest(SQLModel):
    """Request body for the /recommend/profile endpoint."""

    app_ids: Annotated[list[int], Field(min_length=1, max_length=100)]
    hours_played: Annotated[list[Annotated[float, Field(ge=0)]], Field(min_length=1, max_length=100)]
    top_n: Annotated[int, Field(gt=0, le=100)]

    @model_validator(mode="after")
    def check_lengths(self):
        if len(self.app_ids) != len(self.hours_played):
            raise ValueError("app_ids and hours_played must have the same length")
        return self

class ProfileRecommendationResponse(SQLModel):
    """Response wrapper for the /recommend/profile endpoint."""

    recommendations: list[GameRecommendation]

class GameTagResult(SQLModel):
    """Result for a single tag search."""

    app_id: int
    game_name: str
    header_image: str | None
    tags: list[str]
