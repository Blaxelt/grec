from src.feature_engineering import load_features
from sklearn.metrics.pairwise import cosine_similarity

class GameRecommender:
    def __init__(self, data_path, features_path):
        self.df = load_data(data_path, raw=False)
        features = load_features(features_path)
        self.vectors = features['combined_vectors']
        self.wilson_scores = features['wilson_scores']

    def find_similar_games(self, game_name, top_n=10, quality_power=1.0):
        """
        Find similar games using hybrid scoring: similarity × quality^power.
        
        This multiplicative approach ensures:
        - Zero similarity = zero score (irrelevant games never surface)
        - Quality acts as a boost/penalty on relevant games
        
        Args:
            game_name: Name of the target game
            top_n: Number of results to return
            quality_power: Exponent for quality influence (default 1.0)
        
        Returns:
            Dict mapping game indices to their top_n similar game indices,
            or None if no games found
        """
        matches = self.df[self.df['name'].str.lower() == game_name.lower().strip()]
        
        if matches.empty:
            print(f"No game found with name '{game_name}'")
            return None
        
        results = {}
        
        for game_idx in matches.index:
            target_game = self.df.loc[game_idx]
            
            print(f"\nFinding games similar to: {target_game['name']}")
            if 'app_id' in self.df.columns:
                print(f"App ID: {target_game['app_id']}")
            print("-" * 80)
            
            similarities = cosine_similarity([self.vectors[game_idx]], self.vectors)[0]
            
            # Apply multiplicative quality boost
            hybrid_scores = similarities * (self.wilson_scores ** quality_power)
            
            hybrid_scores[game_idx] = -1
            top_indices = hybrid_scores.argsort()[-(top_n):][::-1]
            
            print(f"{'Rank':<5} {'Game Name':<42} {'Hybrid':<9} {'Sim':<9} {'Rating':<12} {'Reviews':<10}")
            print("=" * 90)
            
            for rank, idx in enumerate(top_indices, 1):
                name = self.df.loc[idx, 'name'][:100]
                h_score = hybrid_scores[idx]
                sim_score = similarities[idx]
                
                total_reviews = self.df.loc[idx, 'positive'] + self.df.loc[idx, 'negative']
                rating_pct = (self.df.loc[idx, 'positive'] / total_reviews * 100) if total_reviews > 0 else 0
                
                print(f"{rank:<5} {name:<42} {h_score:.4f}    {sim_score:.4f}    "
                    f"{rating_pct:>5.1f}%       {total_reviews:>,}")
            
            results[game_idx] = top_indices
        
        return results