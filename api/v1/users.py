from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.dependencies import get_current_user
from services.auth_service import AuthService
from schemas.user import User as UserSchema, UserUpdate
from models.user import User

router = APIRouter()

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@router.put("/me", response_model=UserSchema)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    auth_service = AuthService(db)
    updated_user = await auth_service.update_user(str(current_user.id), user_data.dict(exclude_unset=True))
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user

@router.get("/me/orders")
async def get_user_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's orders."""
    # TODO: Implement order service
    return {"message": "Orders endpoint - to be implemented"}

@router.get("/me/wishlist")
async def get_user_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's wishlist."""
    # TODO: Implement wishlist service
    return {"message": "Wishlist endpoint - to be implemented"}

@router.post("/me/wishlist/{book_id}")
async def add_to_wishlist(
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add book to wishlist."""
    # TODO: Implement wishlist service
    return {"message": f"Book {book_id} added to wishlist"}

@router.delete("/me/wishlist/{book_id}")
async def remove_from_wishlist(
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove book from wishlist."""
    # TODO: Implement wishlist service
    return {"message": f"Book {book_id} removed from wishlist"}
