from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc
from decimal import Decimal
from models.book import Book, Category, BookTag
from repositories.base import BaseRepository

class BookRepository(BaseRepository[Book]):
    def __init__(self, db: Session):
        super().__init__(Book, db)

    def get_with_details(self, book_id: str) -> Optional[Book]:
        return (
            self.db.query(Book)
            .options(joinedload(Book.category), joinedload(Book.tags))
            .filter(Book.id == book_id)
            .first()
        )

    def search_books(self, search_params: Dict[str, Any]) -> List[Book]:
        query = self.db.query(Book).options(joinedload(Book.category), joinedload(Book.tags))
        
        # Text search
        if search_params.get("query"):
            search_term = f"%{search_params['query']}%"
            query = query.filter(
                or_(
                    Book.title.ilike(search_term),
                    Book.author.ilike(search_term),
                    Book.isbn.ilike(search_term),
                    Book.publisher.ilike(search_term)
                )
            )
        
        # Category filter
        if search_params.get("category_id"):
            query = query.filter(Book.category_id == search_params["category_id"])
        
        # Price range
        if search_params.get("min_price"):
            query = query.filter(Book.price >= Decimal(str(search_params["min_price"])))
        if search_params.get("max_price"):
            query = query.filter(Book.price <= Decimal(str(search_params["max_price"])))
        
        # Rating filter
        if search_params.get("min_rating"):
            query = query.filter(Book.average_rating >= search_params["min_rating"])
        
        # Author filter
        if search_params.get("author"):
            query = query.filter(Book.author.ilike(f"%{search_params['author']}%"))
        
        # Publisher filter
        if search_params.get("publisher"):
            query = query.filter(Book.publisher.ilike(f"%{search_params['publisher']}%"))
        
        # Year filter
        if search_params.get("published_year"):
            query = query.filter(Book.published_year == search_params["published_year"])
        
        # Sorting
        sort_by = search_params.get("sort_by", "relevance")
        if sort_by == "price_asc":
            query = query.order_by(asc(Book.price))
        elif sort_by == "price_desc":
            query = query.order_by(desc(Book.price))
        elif sort_by == "rating":
            query = query.order_by(desc(Book.average_rating))
        elif sort_by == "newest":
            query = query.order_by(desc(Book.created_at))
        elif sort_by == "oldest":
            query = query.order_by(asc(Book.created_at))
        else:  # relevance
            query = query.order_by(desc(Book.average_rating), desc(Book.total_reviews))
        
        # Pagination
        page = search_params.get("page", 1)
        limit = search_params.get("limit", 20)
        skip = (page - 1) * limit
        
        return query.offset(skip).limit(limit).all()

    def get_books_by_category(self, category_id: str, skip: int = 0, limit: int = 20) -> List[Book]:
        return (
            self.db.query(Book)
            .options(joinedload(Book.category), joinedload(Book.tags))
            .filter(Book.category_id == category_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_popular_books(self, limit: int = 10) -> List[Book]:
        return (
            self.db.query(Book)
            .options(joinedload(Book.category), joinedload(Book.tags))
            .order_by(desc(Book.total_reviews), desc(Book.average_rating))
            .limit(limit)
            .all()
        )

    def get_recent_books(self, limit: int = 10) -> List[Book]:
        return (
            self.db.query(Book)
            .options(joinedload(Book.category), joinedload(Book.tags))
            .order_by(desc(Book.created_at))
            .limit(limit)
            .all()
        )

    def get_books_by_author(self, author: str, limit: int = 10) -> List[Book]:
        return (
            self.db.query(Book)
            .options(joinedload(Book.category), joinedload(Book.tags))
            .filter(Book.author.ilike(f"%{author}%"))
            .limit(limit)
            .all()
        )

class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(Category, db)

    def get_by_slug(self, slug: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.slug == slug).first()

    def get_root_categories(self) -> List[Category]:
        return self.db.query(Category).filter(Category.parent_id.is_(None)).all()

    def get_subcategories(self, parent_id: str) -> List[Category]:
        return self.db.query(Category).filter(Category.parent_id == parent_id).all()

class BookTagRepository(BaseRepository[BookTag]):
    def __init__(self, db: Session):
        super().__init__(BookTag, db)

    def get_by_book_id(self, book_id: str) -> List[BookTag]:
        return self.db.query(BookTag).filter(BookTag.book_id == book_id).all()

    def get_popular_tags(self, limit: int = 20) -> List[str]:
        from sqlalchemy import func
        result = (
            self.db.query(BookTag.tag, func.count(BookTag.tag).label('count'))
            .group_by(BookTag.tag)
            .order_by(desc('count'))
            .limit(limit)
            .all()
        )
        return [tag for tag, count in result]
