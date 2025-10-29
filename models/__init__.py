"""Models package - import all model modules so SQLAlchemy mappers are registered
when the package is imported. This prevents mapper initialization errors caused
by models being defined in separate modules but not imported before mapper
configuration runs.
"""

# Import model classes to ensure mappers are configured
from .book import Book, Category, BookTag
from .user import User
from .review import Review
from .cart import Cart, CartItem
from .order import Order, OrderItem
from .recommendation import UserInteraction, InteractionType

__all__ = [
	"Book",
	"Category",
	"BookTag",
	"User",
	"Review",
	"Cart",
	"CartItem",
	"Order",
	"OrderItem",
	"UserInteraction",
	"InteractionType",
]
