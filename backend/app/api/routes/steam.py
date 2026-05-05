from fastapi import APIRouter, HTTPException, Path
import requests
import os
from app.models import PlayedGameResponse

router = APIRouter(prefix="/steam", tags=["steam"])

STEAM_API_KEY = os.getenv("STEAM_API_KEY")

@router.get("/library/{steam_id}", response_model=list[PlayedGameResponse])
def get_library(
    steam_id: str = Path(..., min_length=1, description="Steam user ID"),
):
    """Get all games in a user's library that has more than 0 hours playtime."""
    if not STEAM_API_KEY:
        raise HTTPException(
            status_code=503, detail="Steam API integration is not configured"
        )

    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": STEAM_API_KEY,
        "steamid": steam_id,
        "include_appinfo": True,
        "include_played_free_games": True,
        "format": "json"
    }
    response = requests.get(url, params=params, timeout=10)
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Steam API request failed")

    data = response.json()
    games = data.get("response", {}).get("games", [])
    played_games = [g for g in games if g.get("playtime_forever", 0) > 0]
    played_games.sort(key=lambda g: g["playtime_forever"], reverse=True)

    return [
        PlayedGameResponse(
            app_id=g["appid"],
            game_name=g["name"],
            hours=round(g["playtime_forever"] / 60, 1)
        ) 
        for g in played_games
    ]
