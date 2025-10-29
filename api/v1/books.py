from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.dependencies import get_current_user, get_current_admin_user
from services.book_service import BookService
from schemas.book import Book, BookCreate, BookUpdate, BookSearch
from models.user import User
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[Book])
async def get_books(
    query: Optional[str] = Query(None, description="Search query"),
    category_id: Optional[str] = Query(None, description="Category ID filter"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    min_rating: Optional[float] = Query(None, description="Minimum rating"),
    author: Optional[str] = Query(None, description="Author filter"),
    publisher: Optional[str] = Query(None, description="Publisher filter"),
    published_year: Optional[int] = Query(None, description="Published year"),
    sort_by: str = Query("relevance", description="Sort by: relevance, price_asc, price_desc, rating, newest"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get books with search and filters."""
    book_service = BookService(db)
    search_params = BookSearch(
        query=query,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        author=author,
        publisher=publisher,
        published_year=published_year,
        sort_by=sort_by,
        page=page,
        limit=limit
    )
    return await book_service.get_books(search_params)


@router.get("/popular", response_model=List[Book])
async def get_popular_books(
    limit: int = Query(10, ge=1, le=50, description="Number of books to return"),
    db: Session = Depends(get_db)
):
    """Get popular books."""
    book_service = BookService(db)
    return await book_service.get_popular_books(limit)


@router.get("/recent", response_model=List[Book])
async def get_recent_books(
    limit: int = Query(10, ge=1, le=50, description="Number of books to return"),
    db: Session = Depends(get_db)
):
    """Get recent books."""
    book_service = BookService(db)
    return await book_service.get_recent_books(limit)


@router.get("/author/{author}", response_model=List[Book])
async def get_books_by_author(
    author: str,
    limit: int = Query(10, ge=1, le=50, description="Number of books to return"),
    db: Session = Depends(get_db)
):
    """Get books by author."""
    book_service = BookService(db)
    return await book_service.get_books_by_author(author, limit)


@router.post("/", response_model=Book)
async def create_book(
    book_data: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new book (admin only)."""
    book_service = BookService(db)
    return await book_service.create_book(book_data)


@router.put("/{book_id}", response_model=Book)
async def update_book(
    book_id: str,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update book (admin only)."""
    book_service = BookService(db)
    book = await book_service.update_book(book_id, book_data)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book


@router.delete("/{book_id}")
async def delete_book(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete book (admin only)."""
    book_service = BookService(db)
    success = await book_service.delete_book(book_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return {"message": "Book deleted successfully"}


@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: UUID, db: Session = Depends(get_db)):
    """Get book by ID."""
    book_service = BookService(db)
    # convert UUID to str for repository lookup (models use UUID/as_uuid=True)
    book = await book_service.get_book_by_id(str(book_id))
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book
