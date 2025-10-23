import numpy as np
from typing import List, Dict, Any, Tuple
from .content_based import ContentBasedRecommender
from .collaborative_filtering import CollaborativeFilteringRecommender

class HybridRecommender:
    def __init__(self, model_path: str = "/app/ml/models"):
        self.model_path = model_path
        self.content_recommender = ContentBasedRecommender(model_path)
        self.collaborative_recommender = CollaborativeFilteringRecommender(model_path)
        
        # Hybrid weights
        self.content_weight = 0.6
        self.collaborative_weight = 0.4
        
    def train(self, books_data: List[Dict[str, Any]], interactions_data: List[Dict[str, Any]]) -> None:
        """Train both content-based and collaborative filtering models."""
        print("Training hybrid recommender...")
        
        # Train content-based model
        self.content_recommender.train(books_data)
        
        # Train collaborative filtering model
        self.collaborative_recommender.train(interactions_data)
        
        print("Hybrid recommender training completed")
    
    def get_user_recommendations(
        self, 
        user_id: str, 
        user_interactions: List[Dict[str, Any]], 
        n_recommendations: int = 10,
        algorithm: str = "hybrid"
    ) -> List[Tuple[str, float]]:
        """Get hybrid recommendations for a user."""
        
        if algorithm == "content":
            return self._get_content_recommendations(user_interactions, n_recommendations)
        elif algorithm == "collaborative":
            return self._get_collaborative_recommendations(user_id, n_recommendations)
        else:  # hybrid
            return self._get_hybrid_recommendations(user_id, user_interactions, n_recommendations)
    
    def get_item_recommendations(
        self, 
        book_id: str, 
        n_recommendations: int = 10,
        algorithm: str = "hybrid"
    ) -> List[Tuple[str, float]]:
        """Get hybrid recommendations for a book."""
        
        if algorithm == "content":
            return self.content_recommender.get_recommendations(book_id, n_recommendations)
        elif algorithm == "collaborative":
            return self.collaborative_recommender.get_item_recommendations(book_id, n_recommendations)
        else:  # hybrid
            return self._get_hybrid_item_recommendations(book_id, n_recommendations)
    
    def _get_content_recommendations(
        self, 
        user_interactions: List[Dict[str, Any]], 
        n_recommendations: int
    ) -> List[Tuple[str, float]]:
        """Get content-based recommendations."""
        try:
            return self.content_recommender.get_user_recommendations(user_interactions, n_recommendations)
        except Exception as e:
            print(f"Error in content-based recommendations: {e}")
            return []
    
    def _get_collaborative_recommendations(
        self, 
        user_id: str, 
        n_recommendations: int
    ) -> List[Tuple[str, float]]:
        """Get collaborative filtering recommendations."""
        try:
            return self.collaborative_recommender.get_user_recommendations(user_id, n_recommendations)
        except Exception as e:
            print(f"Error in collaborative recommendations: {e}")
            return []
    
    def _get_hybrid_recommendations(
        self, 
        user_id: str, 
        user_interactions: List[Dict[str, Any]], 
        n_recommendations: int
    ) -> List[Tuple[str, float]]:
        """Get hybrid recommendations combining both approaches."""
        
        # Get content-based recommendations
        content_recs = self._get_content_recommendations(user_interactions, n_recommendations * 2)
        
        # Get collaborative filtering recommendations
        collab_recs = self._get_collaborative_recommendations(user_id, n_recommendations * 2)
        
        # Combine recommendations
        combined_scores = {}
        
        # Add content-based scores
        for book_id, score in content_recs:
            combined_scores[book_id] = score * self.content_weight
        
        # Add collaborative filtering scores
        for book_id, score in collab_recs:
            if book_id in combined_scores:
                combined_scores[book_id] += score * self.collaborative_weight
            else:
                combined_scores[book_id] = score * self.collaborative_weight
        
        # Sort by combined score
        sorted_recommendations = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_recommendations[:n_recommendations]
    
    def _get_hybrid_item_recommendations(
        self, 
        book_id: str, 
        n_recommendations: int
    ) -> List[Tuple[str, float]]:
        """Get hybrid item recommendations."""
        
        # Get content-based recommendations
        try:
            content_recs = self.content_recommender.get_recommendations(book_id, n_recommendations * 2)
        except Exception as e:
            print(f"Error in content-based item recommendations: {e}")
            content_recs = []
        
        # Get collaborative filtering recommendations
        try:
            collab_recs = self.collaborative_recommender.get_item_recommendations(book_id, n_recommendations * 2)
        except Exception as e:
            print(f"Error in collaborative item recommendations: {e}")
            collab_recs = []
        
        # Combine recommendations
        combined_scores = {}
        
        # Add content-based scores
        for book_id, score in content_recs:
            combined_scores[book_id] = score * self.content_weight
        
        # Add collaborative filtering scores
        for book_id, score in collab_recs:
            if book_id in combined_scores:
                combined_scores[book_id] += score * self.collaborative_weight
            else:
                combined_scores[book_id] = score * self.collaborative_weight
        
        # Sort by combined score
        sorted_recommendations = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_recommendations[:n_recommendations]
    
    def get_cold_start_recommendations(self, n_recommendations: int = 10) -> List[Tuple[str, float]]:
        """Get recommendations for cold start users."""
        try:
            return self.collaborative_recommender.get_cold_start_recommendations(n_recommendations)
        except Exception as e:
            print(f"Error in cold start recommendations: {e}")
            return []
    
    def load_models(self) -> bool:
        """Load both trained models."""
        content_loaded = self.content_recommender.load_model()
        collaborative_loaded = self.collaborative_recommender.load_model()
        
        return content_loaded and collaborative_loaded
    
    def save_models(self) -> None:
        """Save both trained models."""
        self.content_recommender.save_model()
        self.collaborative_recommender.save_model()
    
    def update_weights(self, content_weight: float, collaborative_weight: float) -> None:
        """Update the weights for hybrid recommendations."""
        if abs(content_weight + collaborative_weight - 1.0) > 1e-6:
            raise ValueError("Weights must sum to 1.0")
        
        self.content_weight = content_weight
        self.collaborative_weight = collaborative_weight
