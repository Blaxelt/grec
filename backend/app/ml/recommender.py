from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Game, GameRecommendation


class GameRecommender:

    def find_similar_games(
        self,
        session: Session,
        game_name: str,
        top_n: int = 10,
        quality_power: float = 1.0,
    ) -> tuple[str, list[GameRecommendation]] | None:
        """
        Find similar games using pgvector cosine similarity and Wilson score
        quality boost, computed entirely in the database.

        Hybrid score = cosine_similarity × wilson_score^quality_power

        Args:
            session: Database session.
            game_name: Name of the target game.
            top_n: Number of results to return.
            quality_power: Exponent for quality influence (default 1.0).

        Returns:
            Tuple of (target_game_name, recommendations), or None if not found.
        """
        stmt = select(Game).where(func.lower(Game.game_name) == game_name.strip().lower())
        game = session.exec(stmt).first()

        if not game:
            return None

        similarity = (1 - Game.combined_vector.cosine_distance(game.combined_vector))
        hybrid_score = similarity * func.power(Game.wilson_score, quality_power)

        stmt = (
            select(
                Game.id,
                Game.game_name,
                Game.header_image,
                similarity.label("similarity"),
                Game.wilson_score,
                hybrid_score.label("hybrid_score"),
            )
            .where(Game.id != game.id)
            .order_by(hybrid_score.desc())
            .limit(top_n)
        )
        results = session.exec(stmt).all()

        recommendations = [
            GameRecommendation(
                id=game_id,
                game_name=name,
                header_image=header_img,
                similarity=round(sim, 4),
                wilson_score=round(wilson, 4),
                hybrid_score=round(hybrid, 4),
            )
            for game_id, name, header_img, sim, wilson, hybrid in results
        ]

        return game.game_name, recommendations