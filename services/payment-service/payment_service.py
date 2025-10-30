from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import uuid

from core.config import settings

app = FastAPI(
    title="Payment Service",
    description="Placeholder para processamento de pagamentos",
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

@app.get("/")
async def root():
    return {"message": "Payment Service (Placeholder)", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/payments")
async def process_payment(payment_data: dict):
    """Placeholder para processamento de pagamento"""
    return {
        "payment_id": str(uuid.uuid4()),
        "status": "completed",
        "amount": payment_data.get("amount", 0),
        "order_id": payment_data.get("order_id"),
        "message": "Payment processed successfully (placeholder)"
    }

@app.get("/payment-methods")
async def get_payment_methods():
    """Placeholder para métodos de pagamento"""
    return [
        {
            "id": 1,
            "type": "credit_card",
            "last_four": "****",
            "brand": "visa",
            "is_default": True
        }
    ]

@app.post("/payment-methods")
async def create_payment_method(payment_method: dict):
    """Placeholder para criar método de pagamento"""
    return {
        "id": 2,
        "type": payment_method.get("type", "credit_card"),
        "last_four": "****",
        "brand": "mastercard",
        "is_default": False,
        "message": "Payment method created (placeholder)"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
