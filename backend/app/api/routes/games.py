from fastapi import APIRouter, Query
from sqlalchemy import text

from app.api.deps import SessionDep
from app.models import GameSearchResult

router = APIRouter(prefix="/games", tags=["games"])

@router.get("/search", response_model=list[GameSearchResult])
def search_games(
    session: SessionDep,
    q: str = Query(..., min_length=1, description="Search prefix"),
    limit: int = Query(5, ge=1, le=20),
):
    """Search games by name prefix."""
    rows = session.exec(
        text("SELECT game_name FROM games WHERE game_name ILIKE :prefix ORDER BY game_name LIMIT :lim"),
        params={"prefix": f"{q}%", "lim": limit},
    ).all()

    return [GameSearchResult(game_name=row[0]) for row in rows]
