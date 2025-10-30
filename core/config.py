from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/bookstore"
    DATABASE_POOL_SIZE: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Email (Placeholder - not implemented)
    # SMTP_HOST: str = "smtp.gmail.com"
    # SMTP_PORT: int = 587
    # SMTP_USER: str = "your-email@gmail.com"
    # SMTP_PASSWORD: str = "your-password"
    # SMTP_TLS: bool = True
    # SMTP_SSL: bool = False
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Service URLs
    CATALOG_SERVICE_URL: str = "http://localhost:8001"
    AUTH_SERVICE_URL: str = "http://localhost:8002"
    USERS_SERVICE_URL: str = "http://localhost:8003"
    CART_SERVICE_URL: str = "http://localhost:8004"
    ORDERS_SERVICE_URL: str = "http://localhost:8005"
    PAYMENT_SERVICE_URL: str = "http://localhost:8006"
    RECOMMENDATION_SERVICE_URL: str = "http://localhost:8007"
    
    # Payment (Placeholder)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    
    # Storage (Placeholder - using local uploads)
    # AWS_ACCESS_KEY_ID: str = "your-key"
    # AWS_SECRET_ACCESS_KEY: str = "your-secret"
    # AWS_BUCKET_NAME: str = "bookstore-images"
    # AWS_REGION: str = "us-east-1"
    
    # ML Models
    MODEL_PATH: str = "/app/ml/models"
    RECOMMENDATION_THRESHOLD: float = 0.5
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env

settings = Settings()
