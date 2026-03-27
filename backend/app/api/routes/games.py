from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import Game, GameDetail, GameSearchResult

router = APIRouter(prefix="/games", tags=["games"])

@router.get("/search", response_model=list[GameSearchResult])
def search_games(
    session: SessionDep,
    q: str = Query(..., min_length=1, description="Search prefix"),
    limit: int = Query(5, ge=1, le=20),
):
    """Search games by name prefix."""
    stmt = select(Game.game_name).where(Game.game_name.ilike(f"{q}%")).order_by(Game.game_name).limit(limit)
    rows = session.exec(stmt).all()
    return [GameSearchResult(game_name=name) for name in rows]


@router.get("/{app_id}", response_model=GameDetail)
def get_game(session: SessionDep, app_id: int):
    """Get full details for a single game."""
    game = session.get(Game, app_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    return GameDetail(
        app_id=game.app_id,
        game_name=game.game_name,
        header_image=game.header_image or "",
        short_description=game.short_description,
        genres=game.genres,
        tags=game.tags,
        screenshots=game.screenshots or [],
        wilson_score=game.wilson_score,
    )
