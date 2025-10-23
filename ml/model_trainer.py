import os
import sys
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.book import Book, Category, BookTag
from models.recommendation import UserInteraction
from models.user import User
from .hybrid_recommender import HybridRecommender
from core.config import settings

class ModelTrainer:
    def __init__(self):
        self.db = SessionLocal()
        self.recommender = HybridRecommender(settings.MODEL_PATH)
    
    def prepare_books_data(self) -> List[Dict[str, Any]]:
        """Prepare books data for training."""
        print("Preparing books data...")
        
        books = self.db.query(Book).options(
            Book.category,
            Book.tags
        ).all()
        
        books_data = []
        for book in books:
            book_data = {
                'id': str(book.id),
                'title': book.title,
                'author': book.author,
                'description': book.description or '',
                'publisher': book.publisher,
                'category_name': book.category.name if book.category else '',
                'tags': [tag.tag for tag in book.tags]
            }
            books_data.append(book_data)
        
        print(f"Prepared {len(books_data)} books for training")
        return books_data
    
    def prepare_interactions_data(self) -> List[Dict[str, Any]]:
        """Prepare user interactions data for training."""
        print("Preparing interactions data...")
        
        interactions = self.db.query(UserInteraction).all()
        
        interactions_data = []
        for interaction in interactions:
            interaction_data = {
                'user_id': str(interaction.user_id),
                'book_id': str(interaction.book_id),
                'interaction_value': interaction.interaction_value
            }
            interactions_data.append(interaction_data)
        
        print(f"Prepared {len(interactions_data)} interactions for training")
        return interactions_data
    
    def train_models(self) -> None:
        """Train the recommendation models."""
        print("Starting model training...")
        
        # Prepare data
        books_data = self.prepare_books_data()
        interactions_data = self.prepare_interactions_data()
        
        if not books_data:
            print("No books data available for training")
            return
        
        # Train hybrid recommender
        self.recommender.train(books_data, interactions_data)
        
        print("Model training completed successfully!")
    
    def evaluate_models(self) -> Dict[str, Any]:
        """Evaluate the trained models."""
        print("Evaluating models...")
        
        # TODO: Implement model evaluation
        # This would include metrics like precision@k, recall@k, etc.
        
        evaluation_results = {
            'content_based': {
                'status': 'trained',
                'books_count': len(self.prepare_books_data())
            },
            'collaborative_filtering': {
                'status': 'trained',
                'interactions_count': len(self.prepare_interactions_data())
            },
            'hybrid': {
                'status': 'trained',
                'content_weight': self.recommender.content_weight,
                'collaborative_weight': self.recommender.collaborative_weight
            }
        }
        
        return evaluation_results
    
    def cleanup(self):
        """Clean up database connection."""
        self.db.close()

def main():
    """Main function to train models."""
    trainer = ModelTrainer()
    
    try:
        # Train models
        trainer.train_models()
        
        # Evaluate models
        evaluation_results = trainer.evaluate_models()
        print("Evaluation results:", evaluation_results)
        
    except Exception as e:
        print(f"Error during model training: {e}")
        sys.exit(1)
    finally:
        trainer.cleanup()

if __name__ == "__main__":
    main()
