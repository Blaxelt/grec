
from pathlib import Path

from src.ingestion import load_data
from src.data_cleaning import clean_data, save_data

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def main():
    raw_data_path = PROJECT_ROOT / 'data' / 'raw' / 'games.json'
    clean_data_path = PROJECT_ROOT / 'data' / 'processed' / 'games_cleaned.json'
    
    # Load
    df = load_data(raw_data_path)
    
    # Clean
    cleaned_df = clean_data(df)
    
    # Save
    save_data(cleaned_df, clean_data_path)

if __name__ == '__main__':
    main()
