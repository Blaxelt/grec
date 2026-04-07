from fastapi import APIRouter, HTTPException, Query

from app.api.deps import SessionDep
from app.ml.recommender import GameRecommender
from app.ml.cf_model import CFModel
from app.models import Game, GameRecommendation, RecommendationResponse, ProfileRecommendationResponse, ProfileRequest

router = APIRouter(tags=["recommendations"])

recommender = GameRecommender()
cf_model = CFModel()

@router.get("/recommend", response_model=RecommendationResponse)
def get_recommendations(
    session: SessionDep,
    game: str = Query(..., min_length=1, description="Name of the game to find recommendations for"),
    top_n: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    quality_power: float = Query(1.0, ge=0.0, le=5.0, description="Quality weight exponent"),
):
    """Get similar game recommendations based on content similarity and review quality."""
    result = recommender.find_similar_games(session, game, top_n, quality_power)

    if result is None:
        raise HTTPException(status_code=404, detail=f"Game '{game}' not found")

    target_name, recommendations = result
    return RecommendationResponse(target_game=target_name, recommendations=recommendations)


@router.post("/recommend/profile", response_model=ProfileRecommendationResponse)
def get_profile_recommendations(session: SessionDep, body: ProfileRequest):
    """Get recommendations based on a user profile."""
    result = cf_model.recommend(body.app_ids, body.hours_played, body.top_n)
    
    if result is None:
        raise HTTPException(status_code=404, detail=f"No recommendations found")
    
    recommendations = []
    for app_id, score in result:
        game = session.get(Game, app_id)
        recommendations.append(GameRecommendation(app_id=app_id, game_name=game.game_name, header_image=game.header_image, hybrid_score=score))
        
    return ProfileRecommendationResponse(recommendations=recommendations)
        