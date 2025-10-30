from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx

from core.config import settings
from core.database import get_db, engine, Base
from core.utils import get_current_user_id
from models.recommendation import UserInteraction
from schemas.recommendation import (
    RecommendationResponse, UserInteractionCreate, 
    RecommendationRequest
)
# RecommendationController removed - implementing logic directly

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Recommendation Service",
    description="Serviço de recomendações e sistema de ML",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP client for external service calls
http_client = httpx.AsyncClient()

# Dependency to get recommendation controller
# RecommendationController removed - implementing logic directly

@app.get("/")
async def root():
    return {"message": "Recommendation Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/recommendations")
async def get_recommendations(
    user_id: Optional[int] = None,
    limit: int = 10,
    recommendation_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get recommendations for a user - placeholder implementation"""
    return {"message": "Recommendations retrieved (placeholder)", "user_id": user_id}

@app.post("/recommendations/generate")
async def generate_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """Generate new recommendations for a user"""
    # Simple placeholder implementation
    return {"message": "Recommendations generated (placeholder)", "user_id": request.user_id}

@app.post("/interactions", response_model=dict, status_code=status.HTTP_201_CREATED)
async def record_interaction(
    interaction: UserInteractionCreate,
    db: Session = Depends(get_db)
):
    """Record user interaction (view, like, purchase, etc.)"""
    # Simple placeholder implementation
    return {"message": "Interaction recorded (placeholder)", "interaction": interaction.dict()}

@app.get("/interactions", response_model=List[dict])
async def get_user_interactions(
    interaction_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get user interactions"""
    # Simple placeholder implementation
    return {"message": "User interactions retrieved (placeholder)", "interaction_type": interaction_type}

@app.get("/similar-books/{book_id}")
async def get_similar_books(
    book_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get similar books based on content"""
    # Simple placeholder implementation
    return {"message": "Similar books retrieved (placeholder)", "book_id": book_id}

@app.get("/trending")
async def get_trending_books(
    limit: int = 10,
    time_period: str = "week",
    db: Session = Depends(get_db)
):
    """Get trending books"""
    # Simple placeholder implementation
    return {"message": "Trending books retrieved (placeholder)", "time_period": time_period}

@app.get("/recommendations/explain/{book_id}")
async def explain_recommendation(
    book_id: int,
    db: Session = Depends(get_db)
):
    """Explain why a book was recommended"""
    # Simple placeholder implementation
    return {"message": "Recommendation explanation (placeholder)", "book_id": book_id}

@app.post("/recommendations/feedback")
async def feedback_recommendation(
    book_id: int,
    feedback: str,  # "like", "dislike", "not_interested"
    db: Session = Depends(get_db)
):
    """Provide feedback on a recommendation"""
    # Simple placeholder implementation
    return {"message": "Feedback recorded (placeholder)", "book_id": book_id, "feedback": feedback}

# Admin endpoints
@app.get("/admin/recommendations/stats")
async def get_recommendation_stats(
    db: Session = Depends(get_db)
):
    """Get recommendation statistics (admin only)"""
    # Simple placeholder implementation
    return {"message": "Recommendation stats (placeholder)"}

@app.post("/admin/recommendations/retrain")
async def retrain_models(
    db: Session = Depends(get_db)
):
    """Retrain recommendation models (admin only)"""
    # Simple placeholder implementation
    return {"message": "Models retrained (placeholder)"}

@app.get("/admin/recommendations/performance")
async def get_model_performance(
    db: Session = Depends(get_db)
):
    """Get model performance metrics (admin only)"""
    # Simple placeholder implementation
    return {"message": "Model performance (placeholder)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
