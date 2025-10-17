from dataclasses import dataclass
from typing import List, Dict, Optional
import os
import joblib
from datetime import datetime
import structlog


@dataclass
class Recommendation:
    product_id: int
    score: float


class RecommendationModel:
    """Light wrapper around a pickled ML artifact.

    If no artifact is found the class falls back to a simple popularity mock.
    """

    def __init__(self, model_path: str = "/app/models/recommendation_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.version = None

    def load(self) -> None:
        """Attempt to load a pickled model. If it fails, remain in mock mode."""
        logger = structlog.get_logger()
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                self.version = getattr(self.model, "version", "unknown")
                logger.info("model_loaded", path=self.model_path, version=self.version)
            except Exception as e:
                logger.exception("model_load_failed", path=self.model_path, error=str(e))
                # keep model as None and rely on mock fallback
                self.model = None
        else:
            logger.info("model_not_found", path=self.model_path)
            self.model = None

    def recommend(self, user_id: str, k: int = 10, context: Optional[dict] = None) -> List[Dict]:
        """Return a list of recommendations: [{"product_id": int, "score": float}, ...]

        Behavior:
        - If a loaded artifact exposes `recommend(user_id, k, context)`, use it.
        - Otherwise return a deterministic popularity-based mock.
        """
        logger = structlog.get_logger()
        if self.model is None:
            logger.info("model_fallback_mock", user_id=user_id, k=k)
            return self._mock_recommend(k)

        # Prefer a recommend method on the artifact
        if hasattr(self.model, "recommend"):
            try:
                start = datetime.utcnow()
                recs = self.model.recommend(user_id=user_id, k=k, context=context)
                elapsed_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
                structlog.get_logger().info("model_inference", user_id=user_id, k=k, elapsed_ms=elapsed_ms)
                # Normalize into expected shape
                normalized = []
                for p in recs:
                    # support both dict-like and tuple/list shapes
                    if isinstance(p, dict):
                        pid = int(p.get("product_id") or p.get("id") or p.get("productId"))
                        score = float(p.get("score", 1.0))
                    else:
                        pid = int(p[0])
                        score = float(p[1]) if len(p) > 1 else 1.0
                    normalized.append({"product_id": pid, "score": score})
                return normalized[:k]
            except Exception:
                return self._mock_recommend(k)

        # Fallback to mock
        return self._mock_recommend(k)

    def _mock_recommend(self, k: int) -> List[Dict]:
        now = datetime.utcnow().isoformat() + "Z"
        return [{"product_id": i, "score": 1.0 / (i if i > 0 else 1)} for i in range(1, k + 1)]
