
import numpy as np
import pandas as pd
import psycopg
from pgvector.psycopg import register_vector
import os

from sklearn.preprocessing import normalize, MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfTransformer


# Default weights for combining feature vectors (based on ablation study)
DEFAULT_WEIGHTS = {
    'tags': 0.8,
    'genres': 0.1,
    'descriptions': 0.1,
}


def build_tag_vectors(df: pd.DataFrame) -> np.ndarray:
    """
    Build TF-IDF weighted tag vectors from game tag dictionaries.

    Each game's tags column is expected to be a dict mapping
    tag names to vote counts (e.g. {'Action': 709, 'RPG': 500}).

    Args:
        df: DataFrame with a 'tags' column (dict of tag -> vote count).

    Returns:
        tag_vectors: TF-IDF weighted, L2-normalized tag matrix (n_games, n_tags).
    """
    # Build vocabulary from all tags across all games
    all_tags = set()
    for tags_dict in df['tags']:
        all_tags.update(tags_dict.keys())

    vocab = sorted(all_tags)

    # Create raw tag vectors: log(1 + vote_count)
    def _tag_to_vector(tags_dict):
        vector = np.zeros(len(vocab))
        for i, tag in enumerate(vocab):
            if tag in tags_dict:
                vector[i] = np.log1p(tags_dict[tag])
        return vector

    raw_vectors = np.array([_tag_to_vector(tags) for tags in df['tags']])

    # Apply TF-IDF: down-weight common tags, up-weight rare ones
    tfidf = TfidfTransformer(norm='l2', use_idf=True)
    tag_vectors = tfidf.fit_transform(raw_vectors).toarray()

    return tag_vectors


def build_genre_vectors(df: pd.DataFrame) -> np.ndarray:
    """
    Build multi-hot encoded genre vectors.

    Each game's genres column is expected to be a list of genre strings
    (e.g. ['Action', 'Adventure']).

    Args:
        df: DataFrame with a 'genres' column (list of genre strings).

    Returns:
        genre_vectors: L2-normalized multi-hot genre matrix (n_games, n_genres).
    """
    mlb = MultiLabelBinarizer()
    genre_vectors = mlb.fit_transform(df['genres'])
    genre_vectors = normalize(genre_vectors.astype(float), norm='l2')

    return genre_vectors


def build_description_vectors(df: pd.DataFrame) -> np.ndarray:
    """
    Build sentence-transformer embeddings from game descriptions.

    Uses 'paraphrase-multilingual-MiniLM-L12-v2' to handle descriptions
    in multiple languages present in the Steam dataset.

    Args:
        df: DataFrame with a 'short_description' column.

    Returns:
        description_vectors: L2-normalized embedding matrix (n_games, 384).
    """
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    descriptions = df['short_description'].tolist()

    description_vectors = model.encode(
        descriptions,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    return description_vectors


def build_combined_vectors(
    tag_vectors: np.ndarray,
    genre_vectors: np.ndarray,
    description_vectors: np.ndarray,
    weights: dict[str, float] | None = None,
) -> np.ndarray:
    """
    Combine the three feature vectors into a single composite vector.

    Each component is scaled by its weight before concatenation, and the
    final vector is L2-normalized.

    Args:
        tag_vectors: TF-IDF tag matrix (n_games, n_tags).
        genre_vectors: Multi-hot genre matrix (n_games, n_genres).
        description_vectors: Embedding matrix (n_games, embed_dim).
        weights: Dict with keys 'tags', 'genres', 'descriptions'.
                 Defaults to DEFAULT_WEIGHTS (0.8/0.1/0.1).

    Returns:
        combined: L2-normalized composite feature matrix.
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    combined = np.hstack([
        weights['tags'] * tag_vectors,
        weights['genres'] * genre_vectors,
        weights['descriptions'] * description_vectors,
    ])

    combined = normalize(combined, norm='l2')

    return combined


def calculate_wilson_scores(df: pd.DataFrame, z: float = 1.96) -> np.ndarray:
    """
    Calculate Wilson score lower bound for all games.

    The Wilson score accounts for both the proportion of positive reviews
    and the sample size, making it more reliable than a simple ratio for
    ranking games by quality.

    Args:
        df: DataFrame with 'positive' and 'negative' columns.
        z: Z-score for confidence level (1.96 = 95% confidence).

    Returns:
        Array of Wilson scores, one per game.
    """
    positive = df['positive'].values.astype(float)
    negative = df['negative'].values.astype(float)
    n = positive + negative
    phat = positive / n

    scores = (
        phat + z * z / (2 * n)
        - z * np.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)
    ) / (1 + z * z / n)

    return scores


def engineer_features(
    df: pd.DataFrame,
    weights: dict[str, float] | None = None,
) -> None:
    """
    Run the full feature engineering pipeline and save results to disk.

    Args:
        df: Cleaned DataFrame with columns: name, genres, tags,
            positive, negative, short_description.
        weights: Optional custom weights for combining features.
    """
    print("Building feature vectors...")

    tag_vectors = build_tag_vectors(df)
    print(f"Tag vectors: {tag_vectors.shape}")

    genre_vectors = build_genre_vectors(df)
    print(f"Genre vectors: {genre_vectors.shape}")

    description_vectors = build_description_vectors(df)
    print(f"Description vectors: {description_vectors.shape}")

    combined_vectors = build_combined_vectors(
        tag_vectors, genre_vectors, description_vectors, weights
    )
    print(f"Combined vectors: {combined_vectors.shape}")

    wilson_scores = calculate_wilson_scores(df)
    print(f"Wilson scores: {wilson_scores.shape}")

    save_features(df, combined_vectors, wilson_scores)


def save_features(
    df: pd.DataFrame,
    combined_vectors: np.ndarray,
    wilson_scores: np.ndarray,
) -> None:
    """
    Save pre-computed features to database.
    """
    with psycopg.connect(os.getenv("DATABASE_URL")) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(conn)
        with conn.cursor() as cur:
            vector_dim = combined_vectors.shape[1]
            cur.execute(
                "CREATE TABLE IF NOT EXISTS games ("
                "app_id bigint PRIMARY KEY, "
                "game_name text, "
                "header_image text, "
                "short_description text, "
                "genres text[], "
                "tags text[], "
                "screenshots text[], "
                f"combined_vector vector({vector_dim}), "
                "wilson_score float)"
            )

            data = [
                (
                    int(df.loc[i, 'app_id']),
                    df.loc[i, 'name'],
                    df.loc[i, 'header_image'],
                    df.loc[i, 'short_description'],
                    df.loc[i, 'genres'],
                    list(df.loc[i, 'tags'].keys()),
                    df.loc[i, 'screenshots'] if isinstance(df.loc[i, 'screenshots'], list) else [],
                    combined_vectors[i],
                    float(wilson_scores[i]),
                )
                for i in range(len(combined_vectors))
            ]
            cur.executemany(
                "INSERT INTO games (app_id, game_name, header_image, short_description, genres, tags, screenshots, combined_vector, wilson_score) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                data,
            )
            conn.commit()
            print(f"Successfully inserted {len(data)} games to database.")