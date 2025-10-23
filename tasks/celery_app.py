from celery import Celery
from core.config import settings

# Create Celery app
celery_app = Celery(
    "bookstore",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["tasks.recommendation_tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks
celery_app.conf.beat_schedule = {
    'retrain-recommendation-models': {
        'task': 'tasks.recommendation_tasks.retrain_models',
        'schedule': 86400.0,  # Run daily
    },
    'update-recommendation-cache': {
        'task': 'tasks.recommendation_tasks.update_recommendation_cache',
        'schedule': 3600.0,  # Run hourly
    },
}
