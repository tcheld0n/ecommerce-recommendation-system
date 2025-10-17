from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from .routes import recommendations
from .models.recommendation_model import RecommendationModel
from .logging_config import configure_logging
import time
import structlog


configure_logging()
logger = structlog.get_logger()


app = FastAPI(title="Python Recommendation Service")

app.include_router(recommendations.router, prefix="/api")


@app.middleware("http")
async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = None
        try:
                response = await call_next(request)
                return response
        finally:
                duration_ms = int((time.time() - start_time) * 1000)
                logger.info(
                        "http_request",
                        method=request.method,
                        path=request.url.path,
                        status_code=getattr(response, "status_code", None),
                        duration_ms=duration_ms,
                )


@app.get("/health")
def health():
        return {"status": "ok"}


# Simple debug page: server-side call to the recommendation model and HTML output
model_for_debug = RecommendationModel()
model_for_debug.load()


@app.get("/debug", response_class=HTMLResponse)
def debug_page(request: Request, user_id: str = "1", limit: int = 5):
        """Return a minimal HTML page showing recommendations for quick manual debugging.

        Usage: /debug?user_id=123&limit=5
        """
        try:
                recs = model_for_debug.recommend(user_id=user_id, k=limit)
        except Exception as e:
                logger.exception("recommendation_error", error=str(e), user_id=user_id)
                return HTMLResponse(f"<h1>Error</h1><pre>{e}</pre>", status_code=500)

        items_html = "".join([f"<li>product_id: {r['product_id']} — score: {r['score']}</li>" for r in recs])
        html = f"""
        <html>
                <head><title>Debug Recommendations</title></head>
                <body>
                        <h1>Recommendations (user_id={user_id})</h1>
                        <p>Limit: {limit}</p>
                        <ul>
                                {items_html}
                        </ul>
                        <p><a href="/health">Health</a> | <a href="/api/recommendations/{user_id}?limit={limit}">Raw JSON</a></p>
                </body>
        </html>
        """
        return HTMLResponse(content=html)
