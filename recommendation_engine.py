import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from models import Book, Rating, Purchase, db

class RecommendationEngine:
    """
    Recommendation engine using collaborative filtering and content-based filtering
    """
    
    def __init__(self):
        self.user_item_matrix = None
        self.user_similarity = None
        
    def build_user_item_matrix(self):
        """Build user-item matrix from ratings"""
        ratings = Rating.query.all()
        
        if not ratings:
            return None
            
        data = []
        for rating in ratings:
            data.append({
                'user_id': rating.user_id,
                'book_id': rating.book_id,
                'rating': rating.rating
            })
        
        df = pd.DataFrame(data)
        self.user_item_matrix = df.pivot_table(
            index='user_id',
            columns='book_id',
            values='rating',
            fill_value=0
        )
        return self.user_item_matrix
    
    def calculate_user_similarity(self):
        """Calculate similarity between users based on ratings"""
        if self.user_item_matrix is None:
            self.build_user_item_matrix()
        
        if self.user_item_matrix is None or self.user_item_matrix.empty:
            return None
            
        self.user_similarity = cosine_similarity(self.user_item_matrix)
        return self.user_similarity
    
    def get_collaborative_recommendations(self, user_id, n=5):
        """
        Get book recommendations based on collaborative filtering
        Returns books that similar users liked
        """
        # Build or update matrices
        self.build_user_item_matrix()
        
        if self.user_item_matrix is None or self.user_item_matrix.empty:
            return self.get_popular_books(n)
        
        self.calculate_user_similarity()
        
        # Check if user exists in matrix
        if user_id not in self.user_item_matrix.index:
            return self.get_popular_books(n)
        
        # Get user index
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        
        # Get similar users
        similar_users = self.user_similarity[user_idx]
        
        # Get weighted ratings
        weighted_ratings = np.dot(similar_users, self.user_item_matrix.values)
        
        # Get books user hasn't rated
        user_ratings = self.user_item_matrix.loc[user_id]
        unrated_books = user_ratings[user_ratings == 0].index
        
        # Create recommendations
        recommendations = []
        for book_id in unrated_books:
            book_idx = self.user_item_matrix.columns.get_loc(book_id)
            score = weighted_ratings[book_idx]
            if score > 0:
                recommendations.append((book_id, score))
        
        # Sort by score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        # Get top N books
        recommended_book_ids = [book_id for book_id, _ in recommendations[:n]]
        books = Book.query.filter(Book.id.in_(recommended_book_ids)).all()
        
        return books if books else self.get_popular_books(n)
    
    def get_content_based_recommendations(self, book_id, n=5):
        """
        Get book recommendations based on content similarity
        Returns books in the same genre or by the same author
        """
        book = Book.query.get(book_id)
        if not book:
            return []
        
        # Find books by same author or genre
        recommendations = Book.query.filter(
            db.or_(
                Book.author == book.author,
                Book.genre == book.genre
            ),
            Book.id != book_id
        ).limit(n).all()
        
        return recommendations
    
    def get_popular_books(self, n=5):
        """
        Get popular books based on ratings and purchases
        """
        # Get books with highest average ratings and most purchases
        books = db.session.query(
            Book,
            db.func.avg(Rating.rating).label('avg_rating'),
            db.func.count(Purchase.id).label('purchase_count')
        ).outerjoin(Rating).outerjoin(Purchase).group_by(Book.id).order_by(
            db.desc('avg_rating'),
            db.desc('purchase_count')
        ).limit(n).all()
        
        return [book for book, _, _ in books] if books else Book.query.limit(n).all()
    
    def get_recommendations_for_user(self, user_id, n=5):
        """
        Get personalized recommendations for a user
        Combines collaborative and popular recommendations
        """
        collaborative_recs = self.get_collaborative_recommendations(user_id, n)
        
        # If we don't have enough collaborative recommendations, add popular books
        if len(collaborative_recs) < n:
            popular_books = self.get_popular_books(n - len(collaborative_recs))
            # Filter out books already in recommendations
            collab_ids = {book.id for book in collaborative_recs}
            popular_books = [book for book in popular_books if book.id not in collab_ids]
            collaborative_recs.extend(popular_books[:n - len(collaborative_recs)])
        
        return collaborative_recs[:n]
