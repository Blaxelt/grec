from fastapi import APIRouter, HTTPException, Query

from app.api.deps import SessionDep
from app.ml.recommender import GameRecommender
from app.models import RecommendationResponse

router = APIRouter(tags=["recommendations"])

recommender = GameRecommender()

@router.get("/recommend", response_model=RecommendationResponse)
def get_recommendations(
    session: SessionDep,
    game: str = Query(..., description="Name of the game to find recommendations for"),
    top_n: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    quality_power: float = Query(1.0, ge=0.0, le=5.0, description="Quality weight exponent"),
):
    """Get similar game recommendations based on content similarity and review quality."""
    result = recommender.find_similar_games(session, game, top_n, quality_power)

    if result is None:
        raise HTTPException(status_code=404, detail=f"Game '{game}' not found")

    target_name, recommendations = result
    return RecommendationResponse(target_game=target_name, recommendations=recommendations)
