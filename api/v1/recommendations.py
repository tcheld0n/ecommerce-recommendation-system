from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.dependencies import get_current_user
from schemas.recommendation import RecommendationRequest, RecommendationResponse, BookRecommendation, UserInteractionCreate
from models.user import User
from services.recommendation_service import RecommendationService

router = APIRouter()


@router.post("/interactions", status_code=status.HTTP_201_CREATED)
async def record_interaction(
    payload: UserInteractionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a user interaction (VIEW, ADD_TO_CART, PURCHASE, etc.).

    Exemplo de body: { "book_id": "<uuid>", "interaction_type": "VIEW" }
    """
    service = RecommendationService()
    success = service.record_interaction(str(current_user.id), str(payload.book_id), payload.interaction_type.name, db)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao registrar interação")
    return {"message": "Interaction recorded"}


@router.get("/for-you", response_model=List[BookRecommendation])
async def get_personalized_recommendations(
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    algorithm: str = Query("hybrid", description="Algorithm: content, collaborative, hybrid"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized recommendations for current user."""
    service = RecommendationService()
    recs = service.get_user_recommendations(str(current_user.id), db, limit, algorithm)

    # Map service output to BookRecommendation schema
    result: List[BookRecommendation] = []
    for r in recs:
        result.append(BookRecommendation(
            book_id=r.get('book_id'),
            score=r.get('score', 0.0),
            book={
                'title': r.get('title'),
                'author': r.get('author'),
                'price': r.get('price'),
                'cover_image_url': r.get('cover_image_url')
            }
        ))

    return result


@router.get("/books/{book_id}/similar", response_model=List[BookRecommendation])
async def get_similar_books(
    book_id: str,
    limit: int = Query(10, ge=1, le=50, description="Number of books"),
    algorithm: str = Query("hybrid", description="Algorithm: content, collaborative, hybrid"),
    db: Session = Depends(get_db)
):
    """Get books similar to the specified book."""
    service = RecommendationService()
    recs = service.get_item_recommendations(book_id, db, limit, algorithm)

    result: List[BookRecommendation] = []
    for r in recs:
        result.append(BookRecommendation(
            book_id=r.get('book_id'),
            score=r.get('score', 0.0),
            book={
                'title': r.get('title'),
                'author': r.get('author'),
                'price': r.get('price'),
                'cover_image_url': r.get('cover_image_url')
            }
        ))

    return result
