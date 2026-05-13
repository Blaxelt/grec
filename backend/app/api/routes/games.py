from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select, case, func

from app.api.deps import SessionDep
from app.models import Game, GameDetail, GameSearchResult, GameRecommendation, GameTagResult, PaginatedGameTagResult

from app.ml.cf_model import cf_model
from app.ml.recommender import build_recommendations_from_cf

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

@router.get("/tags", response_model=list[str])
def search_tags(
    session: SessionDep,
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=20),
):
    """Search tags by name."""
    tag_subq = select(func.unnest(Game.tags).label("tag")).subquery()

    stmt = (
        select(tag_subq.c.tag)
        .distinct()
        .where(tag_subq.c.tag.ilike(f"%{q}%"))
        .order_by(tag_subq.c.tag)
        .limit(limit)
    )
    rows = session.exec(stmt).all()
    return [tag for tag in rows]

@router.get("/by-tags", response_model=PaginatedGameTagResult)
def search_games_by_tags(
    session: SessionDep,
    tags: list[str] = Query(..., min_length=1, description="Tags to filter by"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """Search games by tags (AND logic — games must have all selected tags)."""
    where = Game.tags.contains(tags)
    total = session.exec(select(func.count()).select_from(Game).where(where)).one()
    rows = session.exec(
        select(Game.app_id, Game.game_name, Game.header_image, Game.tags)
        .where(where)
        .order_by(Game.wilson_score.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    items = [
        GameTagResult(app_id=app_id, game_name=name, header_image=header_image, tags=row_tags)
        for app_id, name, header_image, row_tags in rows
    ]
    return PaginatedGameTagResult(items=items, total=total, limit=limit, offset=offset)

@router.get("/{app_id}", response_model=GameDetail)
def get_game(session: SessionDep, app_id: int):
    """Get full details for a single game."""
    game = session.get(Game, app_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    cf_results = cf_model.recommend([app_id], [20], 10)
    other_games_recommendations = build_recommendations_from_cf(session, cf_results)

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
