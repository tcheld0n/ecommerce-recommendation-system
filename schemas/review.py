from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class ReviewBase(BaseModel):
    rating: int  # 1-5
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    book_id: UUID

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None

class Review(ReviewBase):
    id: UUID
    user_id: UUID
    book_id: UUID
    helpful_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ReviewWithUser(Review):
    user: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
