from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, SQLModel

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
    combined_vector: list[float] = Field(sa_column=Column(Vector(860)))
    wilson_score: float 


class GameSearchResult(SQLModel):
    """Search result."""

    game_name: str


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


class GameRecommendation(SQLModel):
    """A single recommended game."""

    app_id: int
    game_name: str
    header_image: str | None
    similarity: float
    wilson_score: float
    hybrid_score: float

class RecommendationResponse(SQLModel):
    """Response wrapper for the /recommend endpoint."""

    target_game: str
    recommendations: list[GameRecommendation]