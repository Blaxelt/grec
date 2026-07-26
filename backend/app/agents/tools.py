import logging
from collections.abc import Callable

from sqlalchemy import func
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
    session_factory: Callable[[], Session],
    collector: dict[int, GameRecommendation],
    app_ids: list[int] | None = None,
    hours_played: list[float] | None = None,
) -> list[BaseTool]:
    """Build the game-advisor tools.

    `session_factory` must return a NEW Session on each call: LangGraph
    executes parallel tool calls concurrently in a thread pool, and a
    SQLAlchemy Session is not thread-safe (one connection per session).
    """
    recommender = GameRecommender()

    @tool
    def search_games(query: str) -> str:
        """Look up games by title (partial match). Returns up to 5 titles with
        their app_ids. Use ONLY for title lookups: to resolve a title to an
        app_id for get_game_details, or to confirm exact spelling before
        recommend_similar_games. NOT for genre/mood/theme searches - use
        search_games_by_tags for those."""
        stmt = (
            select(Game.app_id, Game.game_name)
            .where(Game.game_name.ilike(f"%{query}%"))
            .order_by(Game.game_name)
            .limit(5)
        )
        session = session_factory()
        try:
            rows = session.exec(stmt).all()
        finally:
            session.close()
        if not rows:
            return f"No games found matching '{query}'."
        return "\n".join(f"- {name} (app_id: {app_id})" for app_id, name in rows)

    @tool
    def get_game_details(app_id: int) -> str:
        """Get one game's details by app_id: genres, tags, review score (0-1),
        and short description. Use when the user asks about a specific game,
        or to verify a candidate before recommending it."""
        session = session_factory()
        try:
            game = session.get(Game, app_id)
        finally:
            session.close()
        if game is None:
            return f"No game found with app_id {app_id}."
        return _format_details(game)

    @tool
    def search_tags(query: str) -> str:
        """Find official tag names matching a partial word (e.g. "indie" ->
        "Indie", "coop" -> "Co-op"). Returns up to 10 tag names. Use BEFORE
        search_games_by_tags to get exact tag spelling. Tags describe genre,
        mood, theme, length, and player count."""
        tag_subq = select(func.unnest(Game.tags).label("tag")).subquery()
        stmt = (
            select(tag_subq.c.tag)
            .distinct()
            .where(tag_subq.c.tag.ilike(f"%{query}%"))
            .order_by(tag_subq.c.tag)
            .limit(10)
        )
        session = session_factory()
        try:
            rows = session.exec(stmt).all()
        finally:
            session.close()
        if not rows:
            return f"No tags found matching '{query}'."
        return "\n".join(f"- {tag}" for tag in rows)

    @tool
    def search_games_by_tags(tags: list[str], top_n: int = 5) -> str:
        """List the best-reviewed games that have ALL the given tags (AND
        logic), ranked by review score. Use for descriptive requests by genre,
        mood, theme, length, or player count (e.g. tags=["Indie", "Short"]).
        Pass exact tag names - call search_tags first if unsure. NOT for
        title lookups."""
        stmt = (
            select(Game.app_id, Game.game_name, Game.header_image, Game.wilson_score)
            .where(Game.tags.contains(tags))
            .order_by(Game.wilson_score.desc())
            .limit(top_n)
        )
        session = session_factory()
        try:
            rows = session.exec(stmt).all()
        finally:
            session.close()
        if not rows:
            return f"No games found with tags: {', '.join(tags)}."
        recommendations = [
            GameRecommendation(
                app_id=row.app_id,
                game_name=row.game_name,
                header_image=row.header_image,
                hybrid_score=round(float(row.wilson_score), 4),
            )
            for row in rows
        ]
        for r in recommendations:
            collector.setdefault(r.app_id, r)
        return f"Top games tagged {tags}:\n{_format_recommendations(recommendations)}"

    @tool
    def recommend_similar_games(game_name: str, top_n: int = 5) -> str:
        """Recommend games similar to a specific title ("games like X").
        Blends content similarity, review quality, and what other players also
        played. game_name must be the exact title - resolve it with
        search_games first if the spelling is uncertain."""
        session = session_factory()
        try:
            result = recommender.find_similar_games(session, game_name, top_n)
        finally:
            session.close()
        if result is None:
            return f"Game '{game_name}' not found in the database."
        target, recommendations = result
        if not recommendations:
            return f"No similar games found for '{target}'."
        for r in recommendations:
            collector.setdefault(r.app_id, r)
        return f"Games similar to {target}:\n{_format_recommendations(recommendations)}"

    tools: list[BaseTool] = [
        search_games,
        get_game_details,
        search_tags,
        search_games_by_tags,
        recommend_similar_games,
    ]

    if app_ids and hours_played:

        @tool
        def recommend_for_profile(top_n: int = 10) -> str:
            """Recommend games tailored to the user's own taste, based on their
            Steam library (owned games + hours played each). Use ONLY when the
            user asks for personalized picks ("what should I play next?",
            "something for me"). NOT for descriptive requests or "games like
            X"."""
            results = cf_model.recommend(app_ids, hours_played, top_n)
            session = session_factory()
            try:
                recommendations = build_recommendations_from_cf(session, results)
            finally:
                session.close()
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
