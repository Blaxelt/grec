
import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv

from src.ingestion import load_data
from src.data_cleaning import clean_data
from src.feature_engineering import engineer_features
from src.recommender import GameRecommender

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv()

def features_exist() -> bool:
    """Check if the games table already has data."""
    try:
        with psycopg.connect(os.getenv("DATABASE_URL")) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT EXISTS (SELECT 1 FROM games LIMIT 1)")
                return cur.fetchone()[0]
    except Exception:
        return False


def main():
    raw_data_path = PROJECT_ROOT / 'data' / 'raw' / 'games.json'
    clean_data_path = PROJECT_ROOT / 'data' / 'processed' / 'games_cleaned.json'
    
    if not features_exist():
        # Load cleaned data (or run the pipeline to create it)
        if Path(clean_data_path).exists():
            cleaned_df = load_data(clean_data_path, raw=False)
        else:
            df = load_data(raw_data_path)
            cleaned_df = clean_data(df, output_path=clean_data_path)

        # Feature Engineering
        engineer_features(cleaned_df)
    else:
        print("Games vectors already exist in database, skipping pipeline.")

    # Recommendation
    recommender = GameRecommender()
    recommender.find_similar_games("Elden ring")

if __name__ == '__main__':
    main()


