import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv

from pipeline.ingestion import load_data
from pipeline.data_cleaning import clean_data
from pipeline.feature_engineering import engineer_features
from pipeline.collaborative_filtering import (
    train_collaborative_filtering,
    cf_model_exists,
)

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
    
    # ── Content-Based Filtering ──────────────────────────────────────
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
        print("Games vectors already exist in database, skipping content-based pipeline.")

    # ── Collaborative Filtering ──────────────────────────────────────
    
    if not cf_model_exists():
        train_collaborative_filtering()
    else:
        print("CF model already exists, skipping collaborative filtering pipeline.")

if __name__ == '__main__':
    main()