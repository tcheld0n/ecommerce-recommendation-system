import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple
import pickle
import os

class ContentBasedRecommender:
    def __init__(self, model_path: str = "/app/ml/models"):
        self.model_path = model_path
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.book_features = None
        self.similarity_matrix = None
        self.book_ids = None
        
    def prepare_features(self, books_data: List[Dict[str, Any]]) -> np.ndarray:
        """Prepare features for content-based filtering."""
        features = []
        
        for book in books_data:
            # Combine text features
            text_features = []
            
            # Title
            if book.get('title'):
                text_features.append(book['title'])
            
            # Author
            if book.get('author'):
                text_features.append(book['author'])
            
            # Description
            if book.get('description'):
                text_features.append(book['description'])
            
            # Category
            if book.get('category_name'):
                text_features.append(book['category_name'])
            
            # Tags
            if book.get('tags'):
                text_features.extend(book['tags'])
            
            # Publisher
            if book.get('publisher'):
                text_features.append(book['publisher'])
            
            # Combine all text features
            combined_text = ' '.join(text_features)
            features.append(combined_text)
        
        return np.array(features)
    
    def train(self, books_data: List[Dict[str, Any]]) -> None:
        """Train the content-based recommender."""
        print("Training content-based recommender...")
        
        # Prepare features
        text_features = self.prepare_features(books_data)
        
        # Fit TF-IDF vectorizer
        tfidf_matrix = self.vectorizer.fit_transform(text_features)
        
        # Calculate cosine similarity
        self.similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Store book IDs
        self.book_ids = [book['id'] for book in books_data]
        
        # Save model
        self.save_model()
        
        print(f"Content-based model trained with {len(books_data)} books")
    
    def get_recommendations(self, book_id: str, n_recommendations: int = 10) -> List[Tuple[str, float]]:
        """Get content-based recommendations for a book."""
        if self.similarity_matrix is None or self.book_ids is None:
            raise ValueError("Model not trained. Call train() first.")
        
        try:
            book_index = self.book_ids.index(book_id)
        except ValueError:
            raise ValueError(f"Book ID {book_id} not found in training data")
        
        # Get similarity scores for the book
        similarity_scores = self.similarity_matrix[book_index]
        
        # Get top similar books (excluding the book itself)
        similar_indices = np.argsort(similarity_scores)[::-1][1:n_recommendations+1]
        
        recommendations = []
        for idx in similar_indices:
            book_id = self.book_ids[idx]
            score = similarity_scores[idx]
            recommendations.append((book_id, score))
        
        return recommendations
    
    def get_user_recommendations(self, user_interactions: List[Dict[str, Any]], n_recommendations: int = 10) -> List[Tuple[str, float]]:
        """Get content-based recommendations for a user based on their interactions."""
        if self.similarity_matrix is None or self.book_ids is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Calculate user profile based on interactions
        user_profile = np.zeros(len(self.book_ids))
        
        for interaction in user_interactions:
            book_id = interaction['book_id']
            interaction_value = interaction.get('interaction_value', 1.0)
            
            try:
                book_index = self.book_ids.index(book_id)
                user_profile[book_index] += interaction_value
            except ValueError:
                continue
        
        # Normalize user profile
        if np.sum(user_profile) > 0:
            user_profile = user_profile / np.sum(user_profile)
        
        # Calculate similarity between user profile and all books
        user_similarity = np.dot(self.similarity_matrix, user_profile)
        
        # Get top recommendations
        top_indices = np.argsort(user_similarity)[::-1][:n_recommendations]
        
        recommendations = []
        for idx in top_indices:
            book_id = self.book_ids[idx]
            score = user_similarity[idx]
            recommendations.append((book_id, score))
        
        return recommendations
    
    def save_model(self) -> None:
        """Save the trained model."""
        os.makedirs(self.model_path, exist_ok=True)
        
        model_data = {
            'vectorizer': self.vectorizer,
            'similarity_matrix': self.similarity_matrix,
            'book_ids': self.book_ids
        }
        
        with open(os.path.join(self.model_path, 'content_based_model.pkl'), 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self) -> bool:
        """Load the trained model."""
        model_file = os.path.join(self.model_path, 'content_based_model.pkl')
        
        if not os.path.exists(model_file):
            return False
        
        try:
            with open(model_file, 'rb') as f:
                model_data = pickle.load(f)
            
            self.vectorizer = model_data['vectorizer']
            self.similarity_matrix = model_data['similarity_matrix']
            self.book_ids = model_data['book_ids']
            
            return True
        except Exception as e:
            print(f"Error loading content-based model: {e}")
            return False
