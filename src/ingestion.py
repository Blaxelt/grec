import pandas as pd
import shutil
from pathlib import Path  
from typing import Union

import kagglehub

def load_data(file_path: Union[str, Path], raw: bool = True) -> pd.DataFrame:
    """
    Loads game data from a JSON file into a pandas DataFrame.
    If the file does not exist, downloads the Steam games dataset
    from Kaggle using kagglehub and places it in data/raw/.
    
    Args:
        file_path (Union[str, Path]): Path to the dataset file (json).
        raw (bool): Whether the data is raw (True) or cleaned (False).
        
    Returns:
        pd.DataFrame: DataFrame containing the game data.
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        if not raw:
            raise FileNotFoundError(
                f"Cleaned dataset not found: {file_path}. "
                "Run the data cleaning pipeline first to generate it."
            )
        
        print(f"Dataset not found: {file_path}. Downloading dataset from Kaggle...")
        download_path = kagglehub.dataset_download("fronkongames/steam-games-dataset")
        print(f"Dataset downloaded to {download_path}")
        download_path = Path(download_path)
        
        # Ensure the target directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Find the downloaded dataset file and copy it to data/raw/
        downloaded_file = download_path / "games.json"
        if downloaded_file.exists():
            shutil.copy2(downloaded_file, file_path)
            print(f"Dataset saved to {file_path}")
        else:
            raise FileNotFoundError(f"Downloaded dataset at {download_path} does not contain the games.json file.")
    
    print(f"Loading data from {file_path}...")
    
    if raw:
        df = pd.read_json(file_path, orient='index') # index because the json is a dict of dicts
    else:
        df = pd.read_json(file_path, orient='records')
    print(f"Successfully loaded {len(df)} records.")
    return df
