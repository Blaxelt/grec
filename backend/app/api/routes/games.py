from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select, case

from app.api.deps import SessionDep
from app.models import Game, GameDetail, GameSearchResult, GameRecommendation

from app.ml.cf_model import cf_model

router = APIRouter(prefix="/games", tags=["games"])

@router.get("/search", response_model=list[GameSearchResult])
def search_games(
    session: SessionDep,
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(5, ge=1, le=20),
):
    """Search games by name."""
    rank = case(
        (Game.game_name.ilike(f"{q}%"), 0),
        else_=1,
    )
    stmt = (
        select(Game.app_id, Game.game_name)
        .where(Game.game_name.ilike(f"%{q}%"))
        .order_by(rank, Game.game_name)
        .limit(limit)
    )
    rows = session.exec(stmt).all()
    return [GameSearchResult(app_id=app_id, game_name=name) for app_id, name in rows]


@router.get("/{app_id}", response_model=GameDetail)
def get_game(session: SessionDep, app_id: int):
    """Get full details for a single game."""
    game = session.get(Game, app_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    cf_results = cf_model.recommend([app_id], [20], 10)

    rec_app_ids = [rec_id for rec_id, _ in cf_results]
    rec_games = session.exec(select(Game).where(Game.app_id.in_(rec_app_ids))).all()
    scores = {rec_id: score for rec_id, score in cf_results}

    other_games_recommendations = [
        GameRecommendation(
            app_id=g.app_id,
            game_name=g.game_name,
            header_image=g.header_image,
            hybrid_score=scores[g.app_id],
        )
        for g in rec_games
    ]

    return GameDetail(
        app_id=game.app_id,
        game_name=game.game_name,
        header_image=game.header_image or "",
        short_description=game.short_description,
        genres=game.genres,
        tags=game.tags,
        screenshots=game.screenshots or [],
        wilson_score=game.wilson_score,
        other_players_also_played=other_games_recommendations,
    )
