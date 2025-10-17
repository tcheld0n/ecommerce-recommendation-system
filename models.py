from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    genre = db.Column(db.String(50))
    published_year = db.Column(db.Integer)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'price': self.price,
            'description': self.description,
            'genre': self.genre,
            'published_year': self.published_year,
            'stock': self.stock,
            'image_url': self.image_url
        }

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    purchases = db.relationship('Purchase', backref='user', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

class Purchase(db.Model):
    __tablename__ = 'purchases'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    book = db.relationship('Book', backref='purchases')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'purchase_date': self.purchase_date.isoformat()
        }

class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)  # 1-5 stars
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    book = db.relationship('Book', backref='ratings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'rating': self.rating,
            'review': self.review,
            'created_at': self.created_at.isoformat()
        }

class Cart(db.Model):
    __tablename__ = 'cart'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    user = db.relationship('User', backref='cart_items')
    book = db.relationship('Book', backref='cart_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'book': self.book.to_dict() if self.book else None,
            'quantity': self.quantity
        }
