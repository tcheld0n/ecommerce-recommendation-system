from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from repositories.book_repository import BookRepository, CategoryRepository, BookTagRepository
from schemas.book import BookCreate, BookUpdate, BookSearch, CategoryCreate, CategoryUpdate
from models.book import Book, Category, BookTag

class BookService:
    def __init__(self, db: Session):
        self.book_repo = BookRepository(db)
        self.category_repo = CategoryRepository(db)
        self.tag_repo = BookTagRepository(db)

    async def get_books(self, search_params: BookSearch) -> List[Book]:
        """Get books with search and filters."""
        search_dict = search_params.dict()
        return self.book_repo.search_books(search_dict)

    async def get_book_by_id(self, book_id: str) -> Optional[Book]:
        """Get book by ID with details."""
        return self.book_repo.get_with_details(book_id)

    async def create_book(self, book_data: BookCreate) -> Book:
        """Create a new book."""
        book_dict = book_data.dict()
        tags = book_dict.pop("tags", [])
        
        # Create book
        book = self.book_repo.create(book_dict)
        
        # Add tags
        if tags:
            for tag in tags:
                tag_data = {"book_id": str(book.id), "tag": tag}
                self.tag_repo.create(tag_data)
        
        return self.book_repo.get_with_details(str(book.id))

    async def update_book(self, book_id: str, book_data: BookUpdate) -> Optional[Book]:
        """Update book."""
        update_dict = book_data.dict(exclude_unset=True)
        tags = update_dict.pop("tags", None)
        
        # Update book
        book = self.book_repo.update(book_id, update_dict)
        
        # Update tags if provided
        if tags is not None:
            # Remove existing tags
            existing_tags = self.tag_repo.get_by_book_id(book_id)
            for tag in existing_tags:
                self.tag_repo.delete(str(tag.id))
            
            # Add new tags
            for tag in tags:
                tag_data = {"book_id": book_id, "tag": tag}
                self.tag_repo.create(tag_data)
        
        return self.book_repo.get_with_details(book_id)

    async def delete_book(self, book_id: str) -> bool:
        """Delete book."""
        return self.book_repo.delete(book_id)

    async def get_popular_books(self, limit: int = 10) -> List[Book]:
        """Get popular books."""
        return self.book_repo.get_popular_books(limit)

    async def get_recent_books(self, limit: int = 10) -> List[Book]:
        """Get recent books."""
        return self.book_repo.get_recent_books(limit)

    async def get_books_by_category(self, category_id: str, skip: int = 0, limit: int = 20) -> List[Book]:
        """Get books by category."""
        return self.book_repo.get_books_by_category(category_id, skip, limit)

    async def get_books_by_author(self, author: str, limit: int = 10) -> List[Book]:
        """Get books by author."""
        return self.book_repo.get_books_by_author(author, limit)

    # Category methods
    async def get_categories(self) -> List[Category]:
        """Get all categories."""
        return self.category_repo.get_all()

    async def get_category_by_id(self, category_id: str) -> Optional[Category]:
        """Get category by ID."""
        return self.category_repo.get_by_id(category_id)

    async def create_category(self, category_data: CategoryCreate) -> Category:
        """Create a new category."""
        return self.category_repo.create(category_data.dict())

    async def update_category(self, category_id: str, category_data: CategoryUpdate) -> Optional[Category]:
        """Update category."""
        return self.category_repo.update(category_id, category_data.dict(exclude_unset=True))

    async def delete_category(self, category_id: str) -> bool:
        """Delete category."""
        return self.category_repo.delete(category_id)

    async def get_root_categories(self) -> List[Category]:
        """Get root categories."""
        return self.category_repo.get_root_categories()

    async def get_subcategories(self, parent_id: str) -> List[Category]:
        """Get subcategories."""
        return self.category_repo.get_subcategories(parent_id)

    async def get_popular_tags(self, limit: int = 20) -> List[str]:
        """Get popular tags."""
        return self.tag_repo.get_popular_tags(limit)
