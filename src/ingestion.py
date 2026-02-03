import pandas as pd
import os
import json
from pathlib import Path  
from typing import Union

def load_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Loads game data from a JSON file into a pandas DataFrame.
    
    Args:
        file_path (Union[str, Path]): Path to the input JSON file.
        
    Returns:
        pd.DataFrame: DataFrame containing the raw game data.
        
    Raises:
        FileNotFoundError: If the input file does not exist.
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    print(f"Loading data from {file_path}...")
    
    try:
        df = pd.read_json(file_path, orient='index') # index because the json is a dict of dicts
        print(f"Successfully loaded {len(df)} records.")
        return df
    except ValueError as e:
        print(f"Error loading JSON with pandas directly: {e}")
        print("Attempting fallback load method...")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame.from_dict(data, orient='index')
        return df
