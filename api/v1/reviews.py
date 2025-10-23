from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.dependencies import get_current_user
from schemas.review import Review, ReviewCreate, ReviewUpdate
from models.user import User

router = APIRouter()

@router.get("/books/{book_id}", response_model=list[Review])
async def get_book_reviews(
    book_id: str,
    db: Session = Depends(get_db)
):
    """Get reviews for a book."""
    # TODO: Implement review service
    return []

@router.post("/books/{book_id}", response_model=Review)
async def create_review(
    book_id: str,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a review for a book."""
    # TODO: Implement review service
    return {"message": f"Review created for book {book_id}"}

@router.put("/{review_id}", response_model=Review)
async def update_review(
    review_id: str,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a review."""
    # TODO: Implement review service
    return {"message": f"Review {review_id} updated"}

@router.delete("/{review_id}")
async def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a review."""
    # TODO: Implement review service
    return {"message": f"Review {review_id} deleted"}

@router.post("/{review_id}/helpful")
async def mark_review_helpful(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a review as helpful."""
    # TODO: Implement review service
    return {"message": f"Review {review_id} marked as helpful"}
