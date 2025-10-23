from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.dependencies import get_current_admin_user
from services.book_service import BookService
from schemas.book import Category, CategoryCreate, CategoryUpdate
from models.user import User

router = APIRouter()

@router.get("/", response_model=List[Category])
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories."""
    book_service = BookService(db)
    return await book_service.get_categories()

@router.get("/{category_id}", response_model=Category)
async def get_category(category_id: str, db: Session = Depends(get_db)):
    """Get category by ID."""
    book_service = BookService(db)
    category = await book_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.post("/", response_model=Category)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new category (admin only)."""
    book_service = BookService(db)
    return await book_service.create_category(category_data)

@router.put("/{category_id}", response_model=Category)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update category (admin only)."""
    book_service = BookService(db)
    category = await book_service.update_category(category_id, category_data)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete category (admin only)."""
    book_service = BookService(db)
    success = await book_service.delete_category(category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return {"message": "Category deleted successfully"}

@router.get("/{category_id}/books")
async def get_books_by_category(
    category_id: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get books by category."""
    book_service = BookService(db)
    return await book_service.get_books_by_category(category_id, skip, limit)
