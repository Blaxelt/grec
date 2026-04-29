from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Game, GameRecommendation
from app.ml.cf_model import cf_model
    
class GameRecommender:

    def __init__(self) -> None:
        self._cf = cf_model

    def find_similar_games(
        self,
        session: Session,
        game_name: str,
        top_n: int = 10,
        quality_power: float = 1.0,
        hours_played: float = 20.0,
        cf_weight: float = 0.3,
    ) -> tuple[str, list[GameRecommendation]] | None:
        """
        Find similar games using a union-based hybrid of content-based and
        collaborative filtering.

        1. Fetch top-K from CBF (pgvector cosine sim × wilson_score^quality_power)
        2. Fetch top-K from CF  (ALS recalculate_user, rank-based score)
        3. Union both sets; fill missing scores with 0
        4. Min-max normalise each signal to [0, 1]
        5. Hybrid = (1 − cf_weight) · norm_CBF + cf_weight · norm_CF
        6. Rank and return final top_n

        Args:
            session: Database session.
            game_name: Name of the target game.
            top_n: Number of results to return.
            quality_power: Exponent for Wilson score influence (default 1.0).
            hours_played: Hypothetical hours played (default 20.0).
            cf_weight: Weight of the CF score in the final blend
                       (0 → pure CBF, 1 → pure CF). Default 0.3.

        Returns:
            Tuple of (target_game_name, recommendations), or None if not found.
        """
        # Look up target game
        stmt = select(Game).where(func.lower(Game.game_name) == game_name.strip().lower())
        game = session.exec(stmt).first()
        if not game:
            return None

        fetch_k = 50  # Fixed pool so normalization is stable across top_n

        # CBF top-K
        similarity = 1 - Game.combined_vector.cosine_distance(game.combined_vector)
        cbf_score_expr = similarity * func.power(Game.wilson_score, quality_power)

        cbf_stmt = (
            select(Game.app_id, cbf_score_expr.label("cbf_score"))
            .where(Game.app_id != game.app_id)
            .order_by(cbf_score_expr.desc())
            .limit(fetch_k)
        )
        cbf_rows = session.exec(cbf_stmt).all()
        cbf_scores: dict[int, float] = {row.app_id: float(row.cbf_score) for row in cbf_rows}

        # CF top-K
        cf_results = self._cf.recommend([game.app_id], [hours_played], top_n=fetch_k)
        cf_scores: dict[int, float] = {
            app_id: score for app_id, score in cf_results
        }

        # Union
        all_ids = cbf_scores.keys() | cf_scores.keys()
        if not all_ids:
            return game.game_name, []

        # Fill missing with 0
        raw = [
            (aid, cbf_scores.get(aid, 0.0), cf_scores.get(aid, 0.0))
            for aid in all_ids
        ]

        # Min-max normalise each signal
        cbf_vals = [r[1] for r in raw]
        cf_vals  = [r[2] for r in raw]

        cbf_min, cbf_max = min(cbf_vals), max(cbf_vals)
        cf_min,  cf_max  = min(cf_vals),  max(cf_vals)

        # Detect if CF contributed anything
        cf_active = cf_max != cf_min  # False when all zeros

        cbf_range = cbf_max - cbf_min if cbf_max != cbf_min else 1.0 # Avoid division by zero
        cf_range  = cf_max  - cf_min  if cf_active else 1.0

        # Adjust effective weights based on what's actually available
        effective_cbf_w = 1.0 if not cf_active else 1.0 - cf_weight
        effective_cf_w  = 0.0 if not cf_active else cf_weight

        scored: list[tuple[int, float]] = []
        for aid, cbf_raw, cf_raw in raw:
            norm_cbf = (cbf_raw - cbf_min) / cbf_range
            norm_cf  = (cf_raw  - cf_min)  / cf_range
            hybrid   = effective_cbf_w * norm_cbf + effective_cf_w * norm_cf
            scored.append((aid, hybrid))

        # Rank and pick final top-N
        scored.sort(key=lambda x: x[1], reverse=True)
        top_ids = [s[0] for s in scored[:top_n]]
        score_map = {s[0]: s for s in scored[:top_n]}

        # Fetch metadata for the final set
        meta_stmt = select(
            Game.app_id, Game.game_name, Game.header_image,
        ).where(Game.app_id.in_(top_ids))  # type: ignore[union-attr]

        meta_rows = {r.app_id: r for r in session.exec(meta_stmt).all()}

        recommendations = []
        for aid in top_ids:
            meta = meta_rows.get(aid)
            if meta is None:
                continue
            _, hybrid = score_map[aid]
            recommendations.append(
                GameRecommendation(
                    app_id=aid,
                    game_name=meta.game_name,
                    header_image=meta.header_image,
                    hybrid_score=round(hybrid, 4),
                )
            )

        return game.game_name, recommendations