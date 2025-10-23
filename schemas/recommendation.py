from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from models.recommendation import InteractionType

class UserInteractionBase(BaseModel):
    book_id: UUID
    interaction_type: InteractionType
    interaction_value: float = 1.0

class UserInteractionCreate(UserInteractionBase):
    pass

class UserInteraction(UserInteractionBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class RecommendationRequest(BaseModel):
    user_id: Optional[UUID] = None
    book_id: Optional[UUID] = None
    limit: int = 10
    algorithm: Optional[str] = "hybrid"  # content, collaborative, hybrid

class BookRecommendation(BaseModel):
    book_id: UUID
    score: float
    reason: Optional[str] = None
    book: Optional[Dict[str, Any]] = None

class RecommendationResponse(BaseModel):
    recommendations: List[BookRecommendation]
    algorithm_used: str
    generated_at: datetime
