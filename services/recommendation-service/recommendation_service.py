from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
import os

from core.config import settings
from core.database import get_db, engine, Base
from models.recommendation import Recommendation, UserInteraction
from schemas.recommendation import (
    RecommendationResponse, UserInteractionCreate, 
    RecommendationRequest, RecommendationType
)
from infrastructure.adapters.recommendation_controller import RecommendationController

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
def get_recommendation_controller(db: Session = Depends(get_db)) -> RecommendationController:
    return RecommendationController(db)

@app.get("/")
async def root():
    return {"message": "Recommendation Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(
    user_id: Optional[int] = None,
    limit: int = 10,
    recommendation_type: Optional[RecommendationType] = None,
    controller: RecommendationController = Depends(get_recommendation_controller)
):
    """Get recommendations for a user"""
    return await controller.get_recommendations(user_id, limit, recommendation_type)

@app.post("/recommendations/generate")
async def generate_recommendations(
    request: RecommendationRequest,
    controller: RecommendationController = Depends(get_recommendation_controller)
):
    """Generate new recommendations for a user"""
    return await controller.generate_recommendations(request)

@app.post("/interactions", response_model=dict, status_code=status.HTTP_201_CREATED)
async def record_interaction(
    interaction: UserInteractionCreate,
    controller: RecommendationController = Depends(get_recommendation_controller)
):
    """Record user interaction (view, like, purchase, etc.)"""
    return await controller.record_interaction(interaction)

@app.get("/interactions", response_model=List[dict])
async def get_user_interactions(
    interaction_type: Optional[str] = None,
    limit: int = 100,
    controller: RecommendationController = Depends(get_recommendation_controller)
):
    """Get user interactions"""
    return await controller.get_user_interactions(interaction_type, limit)

@app.get("/similar-books/{book_id}")
async def get_similar_books(
    book_id: int,
    limit: int = 10,
    controller: RecommendationController = Depends(get_recommendation_controller)
):
    """Get similar books based on content"""
    return await controller.get_similar_books(book_id, limit)

@app.get("/trending")
async def get_trending_books(
    limit: int = 10,
    time_period: str = "week",
    controller: RecommendationController = Depends(get_recommendation_controller)
):
    """Get trending books"""
    return await controller.get_trending_books(limit, time_period)

@app.get("/recommendations/explain/{book_id}")
async def explain_recommendation(
    book_id: int,
    controller: RecommendationController = Depends(get_recommendation_controller)
):
    """Explain why a book was recommended"""
    return await controller.explain_recommendation(book_id)

@app.post("/recommendations/feedback")
async def feedback_recommendation(
    book_id: int,
    feedback: str,  # "like", "dislike", "not_interested"
    controller: RecommendationController = Depends(get_recommendation_controller)
):
    """Provide feedback on a recommendation"""
    return await controller.feedback_recommendation(book_id, feedback)

# Admin endpoints
@app.get("/admin/recommendations/stats")
async def get_recommendation_stats(
    controller: RecommendationController = Depends(get_recommendation_controller)
):
    """Get recommendation statistics (admin only)"""
    return await controller.get_recommendation_stats()

@app.post("/admin/recommendations/retrain")
async def retrain_models(
    controller: RecommendationController = Depends(get_recommendation_controller)
):
    """Retrain recommendation models (admin only)"""
    return await controller.retrain_models()

@app.get("/admin/recommendations/performance")
async def get_model_performance(
    controller: RecommendationController = Depends(get_recommendation_controller)
):
    """Get model performance metrics (admin only)"""
    return await controller.get_model_performance()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
