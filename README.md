# E-Commerce Book Recommendation System

A comprehensive e-commerce platform for books with an intelligent recommendation engine built using Flask, SQLAlchemy, and machine learning algorithms.

## Features

### Core E-Commerce Features
- **Book Catalog**: Browse and search books by title, author, genre
- **User Management**: User registration and profile management
- **Shopping Cart**: Add, update, and remove books from cart
- **Purchase System**: Complete checkout process with stock management
- **Rating & Reviews**: Rate books and write reviews

### Recommendation Engine
The system includes an intelligent recommendation engine with multiple algorithms:

1. **Collaborative Filtering**: Recommends books based on similar users' preferences
   - Uses user-item rating matrix
   - Calculates user similarity using cosine similarity
   - Suggests books that similar users have rated highly

2. **Content-Based Filtering**: Recommends books similar to ones you've viewed
   - Matches books by genre and author
   - Great for discovering similar titles

3. **Popular Books**: Fallback recommendations based on overall ratings and purchase counts

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tcheld0n/ecommerce-recommendation-system.git
cd ecommerce-recommendation-system
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

The server will start on `http://localhost:5000`

**Note**: By default, the application runs in debug mode for development. For production deployment:
- Set the environment variable `FLASK_DEBUG=0` to disable debug mode
- Use a production WSGI server like Gunicorn or uWSGI instead of the Flask development server

## API Endpoints

### Books
- `GET /api/books` - Get all books (supports filtering by genre, author, search)
- `GET /api/books/<book_id>` - Get specific book details
- `POST /api/books` - Add a new book
- `GET /api/books/<book_id>/ratings` - Get ratings for a book

### Users
- `POST /api/users` - Create a new user
- `GET /api/users/<user_id>` - Get user details

### Shopping Cart
- `GET /api/cart/<user_id>` - Get user's cart
- `POST /api/cart` - Add item to cart
- `PUT /api/cart/<cart_id>` - Update cart item quantity
- `DELETE /api/cart/<cart_id>` - Remove item from cart

### Purchases
- `POST /api/purchase` - Complete purchase from cart
- `GET /api/purchases/<user_id>` - Get user's purchase history

### Ratings
- `POST /api/ratings` - Add or update a book rating

### Recommendations
- `GET /api/recommendations/<user_id>` - Get personalized recommendations
- `GET /api/recommendations/book/<book_id>` - Get similar books
- `GET /api/recommendations/popular` - Get popular books

## Usage Examples

### Search for Books
```bash
curl http://localhost:5000/api/books?genre=Fantasy
curl http://localhost:5000/api/books?search=Harry%20Potter
```

### Create a User
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com"}'
```

### Add to Cart
```bash
curl -X POST http://localhost:5000/api/cart \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "book_id": 1, "quantity": 2}'
```

### Rate a Book
```bash
curl -X POST http://localhost:5000/api/ratings \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "book_id": 1, "rating": 5, "review": "Amazing book!"}'
```

### Get Personalized Recommendations
```bash
curl http://localhost:5000/api/recommendations/1?n=5
```

### Complete Purchase
```bash
curl -X POST http://localhost:5000/api/purchase \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

## Database Schema

### Book
- id, title, author, isbn, price, description, genre, published_year, stock, image_url

### User
- id, username, email

### Purchase
- id, user_id, book_id, quantity, total_price, purchase_date

### Rating
- id, user_id, book_id, rating (1-5), review

### Cart
- id, user_id, book_id, quantity

## Recommendation Algorithm

The recommendation engine uses a hybrid approach:

1. **Collaborative Filtering**: Builds a user-item matrix from ratings and calculates user similarity using cosine similarity. Recommends books that similar users have rated highly.

2. **Content-Based Filtering**: Analyzes book attributes (genre, author) to find similar books.

3. **Popularity-Based**: When user data is insufficient, recommends popular books based on average ratings and purchase counts.

## Sample Data

The application comes pre-loaded with 10 classic and popular books including:
- The Great Gatsby
- To Kill a Mockingbird
- 1984
- Harry Potter and the Sorcerer's Stone
- The Lord of the Rings
- And more...

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Machine Learning**: NumPy, Pandas, Scikit-learn
- **CORS**: Flask-CORS for cross-origin requests

## Development

The project follows a modular structure:
- `app.py`: Main application with API endpoints
- `models.py`: Database models
- `recommendation_engine.py`: Recommendation algorithms
- `requirements.txt`: Python dependencies

## Future Enhancements

Potential improvements for the system:
- User authentication and authorization
- Payment gateway integration
- Advanced search with filters
- Book categories and tags
- Wishlist functionality
- Order tracking
- Email notifications
- Admin dashboard
- Matrix factorization for better recommendations
- Deep learning-based recommendations

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.