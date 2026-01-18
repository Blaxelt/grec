import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and normalizes the game data DataFrame.
    
    Args:
        df (pd.DataFrame): Raw DataFrame containing game data.
        
    Returns:
        pd.DataFrame: Cleaned DataFrame with selected columns and normalized values.
    """
    print("Cleaning data...")
    
    required_cols = [
        'name', 'genres', 'tags', 'short_description', 
        'positive', 'negative', 'metacritic_score', 'developers'
    ]
    
    for col in required_cols:
        if col not in df.columns:
            df[col] = None
            
    # Create a new DataFrame for cleaned data
    cleaned_df = pd.DataFrame()
    
    # 'app_id' is the index in the raw DataFrame
    cleaned_df['app_id'] = df.index
    
    # Normalize 'name'
    cleaned_df['name'] = df['name'].fillna('Unknown')
    
    # Helper to ensure list type
    def ensure_list(x):
        return x if isinstance(x, list) else []

    cleaned_df['genres'] = df['genres'].apply(ensure_list)
    cleaned_df['tags'] = df['tags'].apply(ensure_list)
    
    # Normalize description
    cleaned_df['description'] = df['short_description'].fillna('')
    
    # Numeric fields
    cleaned_df['positive_reviews'] = df['positive'].fillna(0).astype(int)
    cleaned_df['negative_reviews'] = df['negative'].fillna(0).astype(int)
    cleaned_df['metacritic'] = df['metacritic_score'].fillna(0).astype(int)
    
    # Extract first developer
    def get_first_developer(devs):
        if isinstance(devs, list) and len(devs) > 0:
            return devs[0]
        return 'Unknown'
        
    cleaned_df['developer'] = df['developers'].apply(get_first_developer)
    
    print(f"Data cleaned. Resulting shape: {cleaned_df.shape}")
    return cleaned_df

def save_data(df: pd.DataFrame, output_path: str):
    """
    Saves the DataFrame to a JSON file.
    
    Args:
        df (pd.DataFrame): DataFrame to save.
        output_path (str): Destination path.
    """
    print(f"Saving processed data to {output_path}...")
    df.to_json(output_path, orient='records', indent=4, force_ascii=False)
    print("Save complete.")
