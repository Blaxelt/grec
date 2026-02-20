from sqlalchemy import text
from sqlmodel import Session

from app.models import GameRecommendation

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
        # Look up the target game
        row = session.exec(
            text(
                "SELECT id, game_name, combined_vector "
                "FROM games WHERE LOWER(game_name) = LOWER(:name)"
            ),
            params={"name": game_name.strip()},
        ).first()

        if not row:
            return None

        target_id, target_name, target_vector = row

        # Find similar games via pgvector cosine distance
        results = session.exec(
            text("""
                SELECT game_name,
                       1 - (combined_vector <=> :vec) AS similarity,
                       wilson_score,
                       (1 - (combined_vector <=> :vec))
                           * power(wilson_score, :qp) AS hybrid_score
                FROM games
                WHERE id != :tid
                ORDER BY hybrid_score DESC
                LIMIT :topn
            """),
            params={
                "vec": str(target_vector),
                "qp": quality_power,
                "tid": target_id,
                "topn": top_n,
            },
        ).all()

        recommendations = [
            GameRecommendation(
                game_name=name,
                similarity=round(sim, 4),
                wilson_score=round(wilson, 4),
                hybrid_score=round(hybrid, 4),
            )
            for name, sim, wilson, hybrid in results
        ]

        return target_name, recommendations