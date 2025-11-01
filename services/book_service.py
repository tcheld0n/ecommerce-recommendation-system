from typing import Optional, List
from sqlalchemy.orm import Session
from decimal import Decimal
from uuid import UUID
from repositories.book_repository import BookRepository
from schemas.book import BookCreate, BookUpdate, BookSearch
from models.book import Book

class BookService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = BookRepository(db)

    async def get_books(self, search_params: BookSearch) -> List[Book]:
        """Get books with search and filters."""
        # Converte BookSearch para dict para usar no repository
        search_dict = {}
        
        if search_params.query:
            search_dict["query"] = search_params.query
        
        # Category ID pode ser UUID ou string - converte para string
        if search_params.category_id:
            category_id = search_params.category_id
            if isinstance(category_id, UUID):
                search_dict["category_id"] = str(category_id)
            else:
                search_dict["category_id"] = str(category_id)
        
        if search_params.min_price is not None:
            search_dict["min_price"] = float(search_params.min_price)
        
        if search_params.max_price is not None:
            search_dict["max_price"] = float(search_params.max_price)
        
        if search_params.min_rating is not None:
            search_dict["min_rating"] = float(search_params.min_rating)
        
        if search_params.author:
            search_dict["author"] = search_params.author
        
        if search_params.publisher:
            search_dict["publisher"] = search_params.publisher
        
        if search_params.published_year:
            search_dict["published_year"] = search_params.published_year
        
        if search_params.sort_by:
            search_dict["sort_by"] = search_params.sort_by
        
        search_dict["page"] = search_params.page
        search_dict["limit"] = search_params.limit
        
        return self.repository.search_books(search_dict)

    async def get_book_by_id(self, book_id: str) -> Optional[Book]:
        """Get a book by ID."""
        # Tenta converter para UUID se necessário
        try:
            if isinstance(book_id, str):
                book_uuid = UUID(book_id)
            else:
                book_uuid = book_id
            return self.repository.get_with_details(str(book_uuid))
        except (ValueError, AttributeError):
            return self.repository.get_with_details(book_id)

    async def get_popular_books(self, limit: int = 10) -> List[Book]:
        """Get popular books."""
        return self.repository.get_popular_books(limit)

    async def get_recent_books(self, limit: int = 10) -> List[Book]:
        """Get recent books."""
        return self.repository.get_recent_books(limit)

    async def get_books_by_author(self, author: str, limit: int = 10) -> List[Book]:
        """Get books by author."""
        return self.repository.get_books_by_author(author, limit)

    async def get_books_by_category(self, category_id: str, skip: int = 0, limit: int = 20) -> List[Book]:
        """Get books by category."""
        return self.repository.get_books_by_category(category_id, skip, limit)

    async def create_book(self, book_data: BookCreate) -> Book:
        """Create a new book."""
        book_dict = book_data.dict()
        # Remove campos que não são do modelo Book diretamente
        book = Book(**book_dict)
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    async def update_book(self, book_id: str, book_data: BookUpdate) -> Optional[Book]:
        """Update a book."""
        book = self.repository.get_by_id(book_id)
        if not book:
            return None
        
        update_data = book_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(book, field):
                setattr(book, field, value)
        
        self.db.commit()
        self.db.refresh(book)
        return book

    async def delete_book(self, book_id: str) -> bool:
        """Delete a book."""
        book = self.repository.get_by_id(book_id)
        if not book:
            return False
        
        self.db.delete(book)
        self.db.commit()
        return True

    # ===== CATEGORY METHODS =====
    async def get_categories(self) -> List:
        """Get all categories."""
        from models.book import Category
        return self.db.query(Category).all()

    async def get_category_by_id(self, category_id: str):
        """Get category by ID."""
        from models.book import Category
        try:
            if isinstance(category_id, str):
                category_uuid = UUID(category_id)
            else:
                category_uuid = category_id
            return self.db.query(Category).filter(Category.id == category_uuid).first()
        except (ValueError, AttributeError):
            return self.db.query(Category).filter(Category.slug == category_id).first()

    async def create_category(self, category_data):
        """Create a new category."""
        from models.book import Category
        category = Category(**category_data.dict())
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    async def update_category(self, category_id: str, category_data):
        """Update a category."""
        from models.book import Category
        category = await self.get_category_by_id(category_id)
        if not category:
            return None
        
        update_data = category_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(category, field):
                setattr(category, field, value)
        
        self.db.commit()
        self.db.refresh(category)
        return category

    async def delete_category(self, category_id: str) -> bool:
        """Delete a category."""
        category = await self.get_category_by_id(category_id)
        if not category:
            return False
        
        self.db.delete(category)
        self.db.commit()
        return True
