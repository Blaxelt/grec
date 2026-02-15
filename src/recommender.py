import os
import psycopg
from pgvector.psycopg import register_vector

class GameRecommender:
    def __init__(self):
        self.conn_str = os.getenv("DATABASE_URL")

    def find_similar_games(self, game_name, top_n=10, quality_power=1.0):
        """
        Find similar games using pgvector cosine similarity and Wilson score
        quality boost, computed entirely in the database.

        Hybrid score = cosine_similarity × wilson_score^quality_power

        Args:
            game_name: Name of the target game.
            top_n: Number of results to return.
            quality_power: Exponent for quality influence (default 1.0).

        Returns:
            List of result dicts, or None if game not found.
        """
        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor() as cur:
                register_vector(conn)

                # Look up the target game's vector
                cur.execute(
                    "SELECT id, game_name, combined_vector "
                    "FROM games WHERE LOWER(game_name) = LOWER(%s)",
                    (game_name.strip(),),
                )
                matches = cur.fetchall()

                if not matches:
                    print(f"No game found with name '{game_name}'")
                    return None

                results = {}

                for target_id, target_name, target_vector in matches:
                    print(f"\nFinding games similar to: {target_name}")
                    print("-" * 80)

                    cur.execute(
                        """
                        SELECT game_name,
                               1 - (combined_vector <=> %s) AS similarity,
                               wilson_score,
                               (1 - (combined_vector <=> %s))
                                   * power(wilson_score, %s) AS hybrid_score
                        FROM games
                        WHERE id != %s
                        ORDER BY hybrid_score DESC
                        LIMIT %s
                        """,
                        (target_vector, target_vector, quality_power,
                         target_id, top_n),
                    )
                    rows = cur.fetchall()

                    print(
                        f"{'Rank':<5} {'Game Name':<42} {'Hybrid':<9} "
                        f"{'Sim':<9} {'Wilson':<9}"
                    )
                    print("=" * 75)

                    for rank, (name, sim, wilson, hybrid) in enumerate(rows, 1):
                        print(
                            f"{rank:<5} {name[:40]:<42} {hybrid:.4f}    "
                            f"{sim:.4f}    {wilson:.4f}"
                        )

                    results[target_id] = rows

        return results