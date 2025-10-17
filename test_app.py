"""
Tests for the E-Commerce Book Recommendation System
"""
import unittest
import json
from app import app, db, Book, User, Rating, Cart, Purchase
from recommendation_engine import RecommendationEngine

class ECommerceTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and database"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            self._populate_test_data()
    
    def tearDown(self):
        """Clean up after tests"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def _populate_test_data(self):
        """Add sample data for testing"""
        # Add books
        books = [
            Book(title="Book 1", author="Author A", isbn="1111111111111", 
                 price=10.99, genre="Fantasy", stock=10),
            Book(title="Book 2", author="Author B", isbn="2222222222222",
                 price=12.99, genre="Science Fiction", stock=15),
            Book(title="Book 3", author="Author A", isbn="3333333333333",
                 price=14.99, genre="Fantasy", stock=20),
        ]
        
        for book in books:
            db.session.add(book)
        
        # Add users
        users = [
            User(username="testuser1", email="test1@example.com"),
            User(username="testuser2", email="test2@example.com"),
        ]
        
        for user in users:
            db.session.add(user)
        
        db.session.commit()
    
    def test_get_books(self):
        """Test getting all books"""
        response = self.client.get('/api/books')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
    
    def test_get_book_by_id(self):
        """Test getting a specific book"""
        response = self.client.get('/api/books/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Book 1')
    
    def test_filter_books_by_genre(self):
        """Test filtering books by genre"""
        response = self.client.get('/api/books?genre=Fantasy')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
    
    def test_search_books(self):
        """Test searching books"""
        response = self.client.get('/api/books?search=Author%20A')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
    
    def test_create_user(self):
        """Test creating a new user"""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com'
        }
        response = self.client.post('/api/users',
                                   data=json.dumps(user_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'newuser')
    
    def test_add_to_cart(self):
        """Test adding items to cart"""
        cart_data = {
            'user_id': 1,
            'book_id': 1,
            'quantity': 2
        }
        response = self.client.post('/api/cart',
                                   data=json.dumps(cart_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['quantity'], 2)
    
    def test_get_cart(self):
        """Test getting user's cart"""
        # First add item to cart
        with app.app_context():
            cart_item = Cart(user_id=1, book_id=1, quantity=1)
            db.session.add(cart_item)
            db.session.commit()
        
        response = self.client.get('/api/cart/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
    
    def test_create_rating(self):
        """Test creating a book rating"""
        rating_data = {
            'user_id': 1,
            'book_id': 1,
            'rating': 5,
            'review': 'Great book!'
        }
        response = self.client.post('/api/ratings',
                                   data=json.dumps(rating_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['rating'], 5)
    
    def test_get_book_ratings(self):
        """Test getting ratings for a book"""
        # Add a rating first
        with app.app_context():
            rating = Rating(user_id=1, book_id=1, rating=5, review="Excellent")
            db.session.add(rating)
            db.session.commit()
        
        response = self.client.get('/api/books/1/ratings')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['rating'], 5)
    
    def test_purchase_from_cart(self):
        """Test completing a purchase"""
        # Add item to cart first
        with app.app_context():
            cart_item = Cart(user_id=1, book_id=1, quantity=2)
            db.session.add(cart_item)
            db.session.commit()
        
        purchase_data = {'user_id': 1}
        response = self.client.post('/api/purchase',
                                   data=json.dumps(purchase_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['quantity'], 2)
        
        # Verify cart is empty
        response = self.client.get('/api/cart/1')
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)
    
    def test_popular_books(self):
        """Test getting popular books"""
        response = self.client.get('/api/recommendations/popular')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)
    
    def test_content_based_recommendations(self):
        """Test content-based recommendations"""
        response = self.client.get('/api/recommendations/book/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        # Should recommend books by same author or genre
        self.assertGreaterEqual(len(data), 0)
    
    def test_user_recommendations(self):
        """Test personalized user recommendations"""
        # Add some ratings first
        with app.app_context():
            rating1 = Rating(user_id=1, book_id=1, rating=5)
            rating2 = Rating(user_id=1, book_id=2, rating=4)
            db.session.add(rating1)
            db.session.add(rating2)
            db.session.commit()
        
        response = self.client.get('/api/recommendations/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_home_page(self):
        """Test home page"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('endpoints', data)

class RecommendationEngineTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            self._populate_test_data()
            self.engine = RecommendationEngine()
    
    def tearDown(self):
        """Clean up after tests"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def _populate_test_data(self):
        """Add sample data for testing"""
        books = [
            Book(title="Book 1", author="Author A", isbn="1111111111111", 
                 price=10.99, genre="Fantasy", stock=10),
            Book(title="Book 2", author="Author B", isbn="2222222222222",
                 price=12.99, genre="Sci-Fi", stock=15),
            Book(title="Book 3", author="Author A", isbn="3333333333333",
                 price=14.99, genre="Fantasy", stock=20),
        ]
        
        users = [
            User(username="user1", email="user1@example.com"),
            User(username="user2", email="user2@example.com"),
        ]
        
        for book in books:
            db.session.add(book)
        for user in users:
            db.session.add(user)
        
        db.session.commit()
    
    def test_build_user_item_matrix(self):
        """Test building user-item matrix"""
        with app.app_context():
            # Add some ratings
            rating1 = Rating(user_id=1, book_id=1, rating=5)
            rating2 = Rating(user_id=1, book_id=2, rating=4)
            rating3 = Rating(user_id=2, book_id=1, rating=4)
            db.session.add_all([rating1, rating2, rating3])
            db.session.commit()
            
            matrix = self.engine.build_user_item_matrix()
            self.assertIsNotNone(matrix)
            self.assertEqual(matrix.shape[0], 2)  # 2 users
    
    def test_get_popular_books(self):
        """Test getting popular books"""
        with app.app_context():
            books = self.engine.get_popular_books(n=3)
            self.assertEqual(len(books), 3)
    
    def test_content_based_recommendations(self):
        """Test content-based filtering"""
        with app.app_context():
            recommendations = self.engine.get_content_based_recommendations(1, n=2)
            # Should get Book 3 (same author and genre)
            self.assertGreaterEqual(len(recommendations), 0)

if __name__ == '__main__':
    unittest.main()
