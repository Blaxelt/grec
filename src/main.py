
import os
import sys

# Ensure we can import from src if running from root
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ingestion import load_data
from src.preprocessing import clean_data, save_data

def main():
    raw_data_path = 'data/raw/games.json'
    processed_data_path = 'data/processed/games_processed.json'
    
    # Ensure processed directory exists
    os.makedirs(os.path.dirname(processed_data_path), exist_ok=True)
    
    try:
        # Load
        df = load_data(raw_data_path)
        
        # Clean
        cleaned_df = clean_data(df)
        
        # Save
        save_data(cleaned_df, processed_data_path)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
