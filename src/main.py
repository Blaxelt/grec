
from pathlib import Path

from src.ingestion import load_data
from src.data_cleaning import clean_data
from src.feature_engineering import engineer_features
from src.recommender import GameRecommender

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def main():
    raw_data_path = PROJECT_ROOT / 'data' / 'raw' / 'games.json'
    clean_data_path = PROJECT_ROOT / 'data' / 'processed' / 'games_cleaned.json'
    features_dir = PROJECT_ROOT / 'data' / 'processed' / 'features'
    
    # Load
    if not Path(clean_data_path).exists():
        df = load_data(raw_data_path)
    
    # Clean
    if not Path(clean_data_path).exists():
        cleaned_df = clean_data(df, output_path=clean_data_path)
    
    # Feature Engineering
    if not Path(features_dir).exists():
        engineer_features(cleaned_df, features_dir)

    # Recommendation
    recommender = GameRecommender(clean_data_path, features_dir)
    recommender.find_similar_games('Elden Ring')

if __name__ == '__main__':
    main()


