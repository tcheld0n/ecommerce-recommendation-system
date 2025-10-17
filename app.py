from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Book, User, Purchase, Rating, Cart
from recommendation_engine import RecommendationEngine
import os

app = Flask(__name__)
CORS(app)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize recommendation engine
recommendation_engine = RecommendationEngine()

# Books API endpoints
@app.route('/api/books', methods=['GET'])
def get_books():
    """Get all books with optional filtering"""
    genre = request.args.get('genre')
    author = request.args.get('author')
    search = request.args.get('search')
    
    query = Book.query
    
    if genre:
        query = query.filter(Book.genre == genre)
    if author:
        query = query.filter(Book.author.ilike(f'%{author}%'))
    if search:
        query = query.filter(
            db.or_(
                Book.title.ilike(f'%{search}%'),
                Book.author.ilike(f'%{search}%'),
                Book.description.ilike(f'%{search}%')
            )
        )
    
    books = query.all()
    return jsonify([book.to_dict() for book in books])

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a specific book"""
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())

@app.route('/api/books', methods=['POST'])
def create_book():
    """Create a new book"""
    data = request.json
    
    book = Book(
        title=data['title'],
        author=data['author'],
        isbn=data['isbn'],
        price=data['price'],
        description=data.get('description', ''),
        genre=data.get('genre', ''),
        published_year=data.get('published_year'),
        stock=data.get('stock', 0),
        image_url=data.get('image_url', '')
    )
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify(book.to_dict()), 201

# User API endpoints
@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.json
    
    user = User(
        username=data['username'],
        email=data['email']
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

# Cart API endpoints
@app.route('/api/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    """Get user's cart"""
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    return jsonify([item.to_dict() for item in cart_items])

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    data = request.json
    
    # Check if item already in cart
    existing = Cart.query.filter_by(
        user_id=data['user_id'],
        book_id=data['book_id']
    ).first()
    
    if existing:
        existing.quantity += data.get('quantity', 1)
    else:
        cart_item = Cart(
            user_id=data['user_id'],
            book_id=data['book_id'],
            quantity=data.get('quantity', 1)
        )
        db.session.add(cart_item)
    
    db.session.commit()
    
    cart_items = Cart.query.filter_by(user_id=data['user_id']).all()
    return jsonify([item.to_dict() for item in cart_items])

@app.route('/api/cart/<int:cart_id>', methods=['DELETE'])
def remove_from_cart(cart_id):
    """Remove item from cart"""
    cart_item = Cart.query.get_or_404(cart_id)
    user_id = cart_item.user_id
    
    db.session.delete(cart_item)
    db.session.commit()
    
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    return jsonify([item.to_dict() for item in cart_items])

@app.route('/api/cart/<int:cart_id>', methods=['PUT'])
def update_cart(cart_id):
    """Update cart item quantity"""
    cart_item = Cart.query.get_or_404(cart_id)
    data = request.json
    
    cart_item.quantity = data['quantity']
    db.session.commit()
    
    return jsonify(cart_item.to_dict())

# Purchase API endpoints
@app.route('/api/purchase', methods=['POST'])
def create_purchase():
    """Create a purchase from cart"""
    data = request.json
    user_id = data['user_id']
    
    # Get cart items
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    purchases = []
    for item in cart_items:
        book = Book.query.get(item.book_id)
        
        # Check stock
        if book.stock < item.quantity:
            return jsonify({'error': f'Insufficient stock for {book.title}'}), 400
        
        # Create purchase
        purchase = Purchase(
            user_id=user_id,
            book_id=item.book_id,
            quantity=item.quantity,
            total_price=book.price * item.quantity
        )
        
        # Update stock
        book.stock -= item.quantity
        
        db.session.add(purchase)
        purchases.append(purchase)
    
    # Clear cart
    for item in cart_items:
        db.session.delete(item)
    
    db.session.commit()
    
    return jsonify([p.to_dict() for p in purchases]), 201

@app.route('/api/purchases/<int:user_id>', methods=['GET'])
def get_user_purchases(user_id):
    """Get user's purchase history"""
    purchases = Purchase.query.filter_by(user_id=user_id).all()
    return jsonify([p.to_dict() for p in purchases])

# Rating API endpoints
@app.route('/api/ratings', methods=['POST'])
def create_rating():
    """Create or update a book rating"""
    data = request.json
    
    # Check if rating already exists
    existing = Rating.query.filter_by(
        user_id=data['user_id'],
        book_id=data['book_id']
    ).first()
    
    if existing:
        existing.rating = data['rating']
        existing.review = data.get('review', '')
        rating = existing
    else:
        rating = Rating(
            user_id=data['user_id'],
            book_id=data['book_id'],
            rating=data['rating'],
            review=data.get('review', '')
        )
        db.session.add(rating)
    
    db.session.commit()
    
    return jsonify(rating.to_dict()), 201

@app.route('/api/books/<int:book_id>/ratings', methods=['GET'])
def get_book_ratings(book_id):
    """Get all ratings for a book"""
    ratings = Rating.query.filter_by(book_id=book_id).all()
    return jsonify([r.to_dict() for r in ratings])

# Recommendation API endpoints
@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Get personalized recommendations for a user"""
    n = request.args.get('n', default=5, type=int)
    
    recommendations = recommendation_engine.get_recommendations_for_user(user_id, n)
    return jsonify([book.to_dict() for book in recommendations])

@app.route('/api/recommendations/book/<int:book_id>', methods=['GET'])
def get_similar_books(book_id):
    """Get books similar to a given book"""
    n = request.args.get('n', default=5, type=int)
    
    recommendations = recommendation_engine.get_content_based_recommendations(book_id, n)
    return jsonify([book.to_dict() for book in recommendations])

@app.route('/api/recommendations/popular', methods=['GET'])
def get_popular():
    """Get popular books"""
    n = request.args.get('n', default=10, type=int)
    
    books = recommendation_engine.get_popular_books(n)
    return jsonify([book.to_dict() for book in books])

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/')
def index():
    """Home page"""
    return jsonify({
        'message': 'Welcome to the E-Commerce Book Recommendation System',
        'endpoints': {
            'books': '/api/books',
            'users': '/api/users',
            'cart': '/api/cart',
            'purchases': '/api/purchase',
            'ratings': '/api/ratings',
            'recommendations': '/api/recommendations/<user_id>',
            'popular': '/api/recommendations/popular'
        }
    })

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if data already exists
        if Book.query.first():
            return
        
        # Add sample books
        sample_books = [
            Book(title="The Great Gatsby", author="F. Scott Fitzgerald", isbn="9780743273565", 
                 price=12.99, genre="Classic", published_year=1925, stock=50,
                 description="A classic American novel set in the 1920s"),
            Book(title="To Kill a Mockingbird", author="Harper Lee", isbn="9780061120084",
                 price=14.99, genre="Classic", published_year=1960, stock=45,
                 description="A gripping tale of racial injustice and childhood innocence"),
            Book(title="1984", author="George Orwell", isbn="9780451524935",
                 price=13.99, genre="Science Fiction", published_year=1949, stock=60,
                 description="A dystopian social science fiction novel"),
            Book(title="Pride and Prejudice", author="Jane Austen", isbn="9780141439518",
                 price=11.99, genre="Romance", published_year=1813, stock=40,
                 description="A romantic novel of manners"),
            Book(title="The Hobbit", author="J.R.R. Tolkien", isbn="9780547928227",
                 price=15.99, genre="Fantasy", published_year=1937, stock=55,
                 description="A fantasy novel and children's book"),
            Book(title="Harry Potter and the Sorcerer's Stone", author="J.K. Rowling", isbn="9780439708180",
                 price=16.99, genre="Fantasy", published_year=1997, stock=70,
                 description="The first book in the Harry Potter series"),
            Book(title="The Catcher in the Rye", author="J.D. Salinger", isbn="9780316769488",
                 price=13.99, genre="Classic", published_year=1951, stock=35,
                 description="A story about teenage rebellion and angst"),
            Book(title="The Lord of the Rings", author="J.R.R. Tolkien", isbn="9780544003415",
                 price=22.99, genre="Fantasy", published_year=1954, stock=50,
                 description="An epic high-fantasy novel"),
            Book(title="Animal Farm", author="George Orwell", isbn="9780451526342",
                 price=10.99, genre="Classic", published_year=1945, stock=45,
                 description="A satirical allegorical novella"),
            Book(title="Brave New World", author="Aldous Huxley", isbn="9780060850524",
                 price=14.99, genre="Science Fiction", published_year=1932, stock=40,
                 description="A dystopian novel set in a futuristic World State"),
        ]
        
        for book in sample_books:
            db.session.add(book)
        
        # Add sample users
        sample_users = [
            User(username="john_doe", email="john@example.com"),
            User(username="jane_smith", email="jane@example.com"),
            User(username="bob_wilson", email="bob@example.com"),
        ]
        
        for user in sample_users:
            db.session.add(user)
        
        db.session.commit()
        
        print("Database initialized with sample data!")

if __name__ == '__main__':
    init_db()
    # Debug mode should be disabled in production
    # Set environment variable FLASK_DEBUG=0 for production
    debug_mode = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
