
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from ingestion import load_data
from data_cleaning import clean_data, save_data

def main():
    raw_data_path = PROJECT_ROOT / 'data' / 'raw' / 'games.json'
    clean_data_path = PROJECT_ROOT / 'data' / 'processed' / 'games_cleaned.json'
    
    try:
        # Load
        df = load_data(raw_data_path)
        
        # Clean
        cleaned_df = clean_data(df)
        
        # Save
        save_data(cleaned_df, clean_data_path)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
