from fastapi import APIRouter, HTTPException
from typing import List
from ..models.recommendation_model import RecommendationModel

router = APIRouter()

model = RecommendationModel()
model.load()


@router.get("/recommendations/{user_id}")
def get_recommendations(user_id: str, limit: int = 10):
    try:
        recs = model.recommend(user_id=user_id, k=limit)
        return {"user_id": user_id, "recommendations": recs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
