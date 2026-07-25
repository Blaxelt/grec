import logging

from langchain_core.tools import BaseTool, tool
from sqlmodel import Session, select

from app.ml.cf_model import cf_model
from app.ml.recommender import GameRecommender, build_recommendations_from_cf
from app.models import Game, GameRecommendation

logger = logging.getLogger(__name__)

MAX_DESCRIPTION_CHARS = 1000
MAX_TAGS_SHOWN = 15


def _format_details(game: Game) -> str:
    """Human-readable game summary for the LLM, kept short to save tokens."""
    description = game.short_description[:MAX_DESCRIPTION_CHARS]
    tags = ", ".join(game.tags[:MAX_TAGS_SHOWN])
    return (
        f"{game.game_name} (app_id: {game.app_id})\n"
        f"Genres: {', '.join(game.genres)}\n"
        f"Tags: {tags}\n"
        f"Review score: {game.wilson_score:.2f} (0-1, higher is better)\n"
        f"Description: {description}"
    )


def _format_recommendations(recommendations: list[GameRecommendation]) -> str:
    return "\n".join(
        f"- {r.game_name} (app_id: {r.app_id}, score: {r.hybrid_score:.2f})"
        for r in recommendations
    )


def make_tools(
    session: Session,
    collector: dict[int, GameRecommendation],
    app_ids: list[int] | None = None,
    hours_played: list[float] | None = None,
) -> list[BaseTool]:
    """Build the game-advisor tools bound to a DB session."""
    
    recommender = GameRecommender()

    @tool
    def search_games(query: str) -> str:
        """Search for games in the database by (partial) name. Returns matching
        game names with their app_ids. Use this to resolve a game title to an
        app_id before calling get_game_details."""
        stmt = (
            select(Game.app_id, Game.game_name)
            .where(Game.game_name.ilike(f"%{query}%"))
            .order_by(Game.game_name)
            .limit(5)
        )
        rows = session.exec(stmt).all()
        if not rows:
            return f"No games found matching '{query}'."
        return "\n".join(f"- {name} (app_id: {app_id})" for app_id, name in rows)

    @tool
    def get_game_details(app_id: int) -> str:
        """Get details about a specific game (genres, tags, review score,
        description) by its app_id."""
        game = session.get(Game, app_id)
        if game is None:
            return f"No game found with app_id {app_id}."
        return _format_details(game)

    @tool
    def recommend_similar_games(game_name: str, top_n: int = 5) -> str:
        """Recommend games similar to the given game title, using content
        similarity, review quality and what other players also played.
        game_name must be the exact title; use search_games first if unsure."""
        result = recommender.find_similar_games(session, game_name, top_n)
        if result is None:
            return f"Game '{game_name}' not found in the database."
        target, recommendations = result
        if not recommendations:
            return f"No similar games found for '{target}'."
        for r in recommendations:
            collector.setdefault(r.app_id, r)
        return f"Games similar to {target}:\n{_format_recommendations(recommendations)}"

    tools: list[BaseTool] = [search_games, get_game_details, recommend_similar_games]

    if app_ids and hours_played:

        @tool
        def recommend_for_profile(top_n: int = 10) -> str:
            """Recommend games personalized to the user based on their Steam
            library (the games they own and how long they played each). Use this
            when the user asks for recommendations tailored to their taste."""
            results = cf_model.recommend(app_ids, hours_played, top_n)
            recommendations = build_recommendations_from_cf(session, results)
            if not recommendations:
                return "No personalized recommendations available for this library."
            for r in recommendations:
                collector.setdefault(r.app_id, r)
            return (
                "Personalized recommendations based on the user's library:\n"
                + _format_recommendations(recommendations)
            )

        tools.append(recommend_for_profile)

    return tools
