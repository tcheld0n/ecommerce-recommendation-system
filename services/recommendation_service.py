from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.book import Book
from models.user import User
from models.recommendation import UserInteraction
from ml.hybrid_recommender import HybridRecommender
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self):
        self.recommender = HybridRecommender(settings.MODEL_PATH)
        self._load_models()
    
    def _load_models(self) -> bool:
        """Load trained models."""
        try:
            return self.recommender.load_models()
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False
    
    def get_user_recommendations(
        self, 
        user_id: str, 
        db: Session, 
        limit: int = 10, 
        algorithm: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user."""
        try:
            # Get user interactions
            user_interactions = self._get_user_interactions(user_id, db)
            
            # Get recommendations from ML model
            if algorithm == "content":
                recommendations = self.recommender.content_recommender.get_user_recommendations(
                    user_interactions, limit
                )
            elif algorithm == "collaborative":
                recommendations = self.recommender.collaborative_recommender.get_user_recommendations(
                    user_id, limit
                )
            else:  # hybrid
                recommendations = self.recommender.get_user_recommendations(
                    user_id, user_interactions, limit, algorithm
                )
            
            # Convert to book details
            book_recommendations = []
            for book_id, score in recommendations:
                book = db.query(Book).filter(Book.id == book_id).first()
                if book:
                    book_recommendations.append({
                        'book_id': str(book.id),
                        'title': book.title,
                        'author': book.author,
                        'price': float(book.price),
                        'cover_image_url': book.cover_image_url,
                        'average_rating': book.average_rating,
                        'score': float(score)
                    })
            
            return book_recommendations
            
        except Exception as e:
            logger.error(f"Error getting user recommendations: {e}")
            # Fallback to trending books
            return self._get_trending_books(db, limit)
    
    def get_item_recommendations(
        self, 
        book_id: str, 
        db: Session, 
        limit: int = 10, 
        algorithm: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """Get recommendations for a specific book."""
        try:
            # Get recommendations from ML model
            if algorithm == "content":
                recommendations = self.recommender.content_recommender.get_recommendations(
                    book_id, limit
                )
            elif algorithm == "collaborative":
                recommendations = self.recommender.collaborative_recommender.get_item_recommendations(
                    book_id, limit
                )
            else:  # hybrid
                recommendations = self.recommender.get_item_recommendations(
                    book_id, limit, algorithm
                )
            
            # Convert to book details
            book_recommendations = []
            for rec_book_id, score in recommendations:
                book = db.query(Book).filter(Book.id == rec_book_id).first()
                if book:
                    book_recommendations.append({
                        'book_id': str(book.id),
                        'title': book.title,
                        'author': book.author,
                        'price': float(book.price),
                        'cover_image_url': book.cover_image_url,
                        'average_rating': book.average_rating,
                        'score': float(score)
                    })
            
            return book_recommendations
            
        except Exception as e:
            logger.error(f"Error getting item recommendations: {e}")
            # Fallback to trending books
            return self._get_trending_books(db, limit)
    
    def get_trending_books(self, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending books based on recent interactions."""
        return self._get_trending_books(db, limit)
    
    def get_cold_start_recommendations(self, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recommendations for new users (cold start problem)."""
        try:
            # Get cold start recommendations from ML model
            recommendations = self.recommender.get_cold_start_recommendations(limit)
            
            # Convert to book details
            book_recommendations = []
            for book_id, score in recommendations:
                book = db.query(Book).filter(Book.id == book_id).first()
                if book:
                    book_recommendations.append({
                        'book_id': str(book.id),
                        'title': book.title,
                        'author': book.author,
                        'price': float(book.price),
                        'cover_image_url': book.cover_image_url,
                        'average_rating': book.average_rating,
                        'score': float(score)
                    })
            
            return book_recommendations
            
        except Exception as e:
            logger.error(f"Error getting cold start recommendations: {e}")
            # Fallback to trending books
            return self._get_trending_books(db, limit)
    
    def _get_user_interactions(self, user_id: str, db: Session) -> List[Dict[str, Any]]:
        """Get user interactions for ML model."""
        interactions = db.query(UserInteraction).filter(
            UserInteraction.user_id == user_id
        ).all()
        
        return [
            {
                'book_id': str(interaction.book_id),
                'interaction_value': interaction.interaction_value or 1.0
            }
            for interaction in interactions
        ]
    
    def _get_trending_books(self, db: Session, limit: int) -> List[Dict[str, Any]]:
        """Fallback method to get trending books."""
        # Get books with highest ratings and most reviews
        books = db.query(Book).filter(
            Book.average_rating > 0
        ).order_by(
            Book.average_rating.desc(),
            Book.total_reviews.desc()
        ).limit(limit).all()
        
        return [
            {
                'book_id': str(book.id),
                'title': book.title,
                'author': book.author,
                'price': float(book.price),
                'cover_image_url': book.cover_image_url,
                'average_rating': book.average_rating,
                'score': float(book.average_rating)
            }
            for book in books
        ]
    
    def record_interaction(
        self, 
        user_id: str, 
        book_id: str, 
        interaction_type: str, 
        db: Session
    ) -> bool:
        """Record user interaction for future recommendations."""
        try:
            # Map interaction types to values
            interaction_values = {
                'VIEW': 1.0,
                'ADD_TO_CART': 2.0,
                'PURCHASE': 5.0,
                'REVIEW': 3.0,
                'WISHLIST': 2.5
            }
            
            interaction_value = interaction_values.get(interaction_type, 1.0)
            
            # Create or update interaction
            existing_interaction = db.query(UserInteraction).filter(
                UserInteraction.user_id == user_id,
                UserInteraction.book_id == book_id
            ).first()
            
            if existing_interaction:
                existing_interaction.interaction_value = interaction_value
            else:
                new_interaction = UserInteraction(
                    user_id=user_id,
                    book_id=book_id,
                    interaction_type=interaction_type,
                    interaction_value=interaction_value
                )
                db.add(new_interaction)
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error recording interaction: {e}")
            db.rollback()
            return False
