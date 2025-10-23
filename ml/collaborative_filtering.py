import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors
from typing import List, Dict, Any, Tuple
import pickle
import os

class CollaborativeFilteringRecommender:
    def __init__(self, model_path: str = "/app/ml/models"):
        self.model_path = model_path
        self.user_item_matrix = None
        self.user_ids = None
        self.item_ids = None
        self.svd_model = None
        self.knn_model = None
        
    def prepare_user_item_matrix(self, interactions_data: List[Dict[str, Any]]) -> np.ndarray:
        """Prepare user-item interaction matrix."""
        # Create DataFrame from interactions
        df = pd.DataFrame(interactions_data)
        
        if df.empty:
            return np.array([])
        
        # Get unique users and items
        self.user_ids = df['user_id'].unique().tolist()
        self.item_ids = df['book_id'].unique().tolist()
        
        # Create user-item matrix
        user_item_matrix = np.zeros((len(self.user_ids), len(self.item_ids)))
        
        # Fill matrix with interaction values
        for _, row in df.iterrows():
            user_idx = self.user_ids.index(row['user_id'])
            item_idx = self.item_ids.index(row['book_id'])
            user_item_matrix[user_idx, item_idx] = row.get('interaction_value', 1.0)
        
        return user_item_matrix
    
    def train(self, interactions_data: List[Dict[str, Any]]) -> None:
        """Train the collaborative filtering recommender."""
        print("Training collaborative filtering recommender...")
        
        if not interactions_data:
            print("No interaction data available for training")
            return
        
        # Prepare user-item matrix
        self.user_item_matrix = self.prepare_user_item_matrix(interactions_data)
        
        if self.user_item_matrix.size == 0:
            print("Empty user-item matrix")
            return
        
        # Train SVD model for matrix factorization
        n_components = min(50, min(self.user_item_matrix.shape) - 1)
        if n_components > 0:
            self.svd_model = TruncatedSVD(n_components=n_components, random_state=42)
            user_factors = self.svd_model.fit_transform(self.user_item_matrix)
            
            # Train KNN model for user-based recommendations
            self.knn_model = NearestNeighbors(n_neighbors=min(20, len(self.user_ids)), metric='cosine')
            self.knn_model.fit(user_factors)
        
        # Save model
        self.save_model()
        
        print(f"Collaborative filtering model trained with {len(interactions_data)} interactions")
    
    def get_user_recommendations(self, user_id: str, n_recommendations: int = 10) -> List[Tuple[str, float]]:
        """Get collaborative filtering recommendations for a user."""
        if self.user_item_matrix is None or self.svd_model is None or self.knn_model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        try:
            user_idx = self.user_ids.index(user_id)
        except ValueError:
            raise ValueError(f"User ID {user_id} not found in training data")
        
        # Get user's interaction history
        user_interactions = self.user_item_matrix[user_idx]
        
        # Find similar users
        user_factors = self.svd_model.transform(self.user_item_matrix[user_idx:user_idx+1])
        distances, indices = self.knn_model.kneighbors(user_factors)
        
        # Calculate recommendations based on similar users
        recommendations = {}
        
        for i, similar_user_idx in enumerate(indices[0]):
            if similar_user_idx == user_idx:  # Skip the user themselves
                continue
            
            similar_user_interactions = self.user_item_matrix[similar_user_idx]
            weight = 1.0 / (distances[0][i] + 1e-6)  # Inverse distance as weight
            
            # Add weighted interactions from similar users
            for item_idx, interaction_value in enumerate(similar_user_interactions):
                if interaction_value > 0 and user_interactions[item_idx] == 0:  # Item not interacted by user
                    item_id = self.item_ids[item_idx]
                    if item_id not in recommendations:
                        recommendations[item_id] = 0
                    recommendations[item_id] += interaction_value * weight
        
        # Sort by score and return top recommendations
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return sorted_recommendations[:n_recommendations]
    
    def get_item_recommendations(self, book_id: str, n_recommendations: int = 10) -> List[Tuple[str, float]]:
        """Get item-based collaborative filtering recommendations."""
        if self.user_item_matrix is None:
            raise ValueError("Model not trained. Call train() first.")
        
        try:
            item_idx = self.item_ids.index(book_id)
        except ValueError:
            raise ValueError(f"Book ID {book_id} not found in training data")
        
        # Calculate item-item similarity using cosine similarity
        item_vector = self.user_item_matrix[:, item_idx]
        
        similarities = []
        for other_item_idx, other_item_id in enumerate(self.item_ids):
            if other_item_idx == item_idx:
                continue
            
            other_item_vector = self.user_item_matrix[:, other_item_idx]
            
            # Calculate cosine similarity
            dot_product = np.dot(item_vector, other_item_vector)
            norm_a = np.linalg.norm(item_vector)
            norm_b = np.linalg.norm(other_item_vector)
            
            if norm_a == 0 or norm_b == 0:
                similarity = 0
            else:
                similarity = dot_product / (norm_a * norm_b)
            
            similarities.append((other_item_id, similarity))
        
        # Sort by similarity and return top recommendations
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:n_recommendations]
    
    def get_cold_start_recommendations(self, n_recommendations: int = 10) -> List[Tuple[str, float]]:
        """Get recommendations for cold start users (most popular items)."""
        if self.user_item_matrix is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Calculate item popularity (sum of interactions)
        item_popularity = np.sum(self.user_item_matrix, axis=0)
        
        # Get top popular items
        popular_indices = np.argsort(item_popularity)[::-1]
        
        recommendations = []
        for idx in popular_indices[:n_recommendations]:
            item_id = self.item_ids[idx]
            popularity_score = item_popularity[idx]
            recommendations.append((item_id, popularity_score))
        
        return recommendations
    
    def save_model(self) -> None:
        """Save the trained model."""
        os.makedirs(self.model_path, exist_ok=True)
        
        model_data = {
            'user_item_matrix': self.user_item_matrix,
            'user_ids': self.user_ids,
            'item_ids': self.item_ids,
            'svd_model': self.svd_model,
            'knn_model': self.knn_model
        }
        
        with open(os.path.join(self.model_path, 'collaborative_model.pkl'), 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self) -> bool:
        """Load the trained model."""
        model_file = os.path.join(self.model_path, 'collaborative_model.pkl')
        
        if not os.path.exists(model_file):
            return False
        
        try:
            with open(model_file, 'rb') as f:
                model_data = pickle.load(f)
            
            self.user_item_matrix = model_data['user_item_matrix']
            self.user_ids = model_data['user_ids']
            self.item_ids = model_data['item_ids']
            self.svd_model = model_data['svd_model']
            self.knn_model = model_data['knn_model']
            
            return True
        except Exception as e:
            print(f"Error loading collaborative filtering model: {e}")
            return False
