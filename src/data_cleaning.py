import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the games dataset by removing invalid entries and handling duplicates.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Raw dataframe with game data
        
    Returns:
    --------
    pd.DataFrame
        Cleaned dataframe ready for processing
    """
    # Select potential columns needed for the system
    cols_to_keep = ['name', 'genres', 'tags', 'positive', 'negative', 'short_description']
    df = df[cols_to_keep].copy()
    
    # Remove rows with empty name
    df = df[df['name'].str.strip() != '']
    
    # Remove rows with empty genres
    df = df[df['genres'].str.len() > 0]
    
    # Remove rows with empty tags
    df = df[df['tags'].str.len() > 0]
    
    # Remove rows with 0 positive or 0 negative reviews
    df = df[(df['positive'] > 0) & (df['negative'] > 0)]
    
    # Remove rows with empty short description
    df = df[df['short_description'].str.strip() != '']
    
    # Remove games with less than 100 reviews
    df = df[df['positive'] + df['negative'] >= 100]
    
    # Handle duplicates
    df = _remove_redundant_duplicates(df)

    df = df.reset_index().rename(columns={'index': 'app_id'})
    
    return df


def _remove_redundant_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove redundant duplicate entries, keeping:
    - All games with same name but different descriptions (different games)
    - Only the version with most reviews for same game snapshots
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe potentially containing duplicates
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with redundant duplicates removed
    """
    # Identify duplicates by name
    duplicated_names = df[df['name'].duplicated(keep=False)]['name'].unique()
    
    rows_to_keep = []
    
    for name in duplicated_names:
        subset = df[df['name'] == name].copy()
        
        # Clean descriptions for comparison
        subset['desc_clean'] = (
            subset['short_description']
            .str.lower()
            .str.strip()
            .str.replace(r'\s+', ' ', regex=True)
        )
        
        # Check if short_description differs (different games with same name)
        if subset['desc_clean'].nunique() > 1:
            # Keep all - they are different games
            rows_to_keep.extend(subset.index.tolist())
        else:
            # Same game, different snapshots - keep the one with most reviews
            subset['total_reviews'] = subset['positive'] + subset['negative']
            best_idx = subset['total_reviews'].idxmax()
            rows_to_keep.append(best_idx)
    
    # Keep all non-duplicated rows
    non_duplicated = df[~df['name'].duplicated(keep=False)].index.tolist()
    rows_to_keep.extend(non_duplicated)
    
    # Create cleaned dataframe
    df_cleaned = df.loc[rows_to_keep].copy()
    
    return df_cleaned


def save_data(df: pd.DataFrame, output_path: Union[str, Path]):
    """
    Saves the DataFrame to a JSON file.
    
    Args:
        df (pd.DataFrame): DataFrame to save.
        output_path (Union[str, Path]): Destination path.
    """
    output_path = Path(output_path)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Saving processed data to {output_path}...")
    df.to_json(output_path, orient='records', indent=4, force_ascii=False)
    print("Save complete.")
