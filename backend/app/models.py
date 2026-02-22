from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field, SQLModel

class Game(SQLModel, table=True):
    """Maps to the existing 'games' table created by the pipeline."""

    __tablename__ = "games"

    id: int | None = Field(default=None, primary_key=True)
    game_name: str
    header_image: str
    combined_vector: list[float] = Field(sa_column=Column(Vector(860)))
    wilson_score: float


class GameSearchResult(SQLModel):
    """Search result."""

    game_name: str


class GameRecommendation(SQLModel):
    """A single recommended game."""

    game_name: str
    header_image: str
    similarity: float
    wilson_score: float
    hybrid_score: float

class RecommendationResponse(SQLModel):
    """Response wrapper for the /recommend endpoint."""

    target_game: str
    recommendations: list[GameRecommendation]