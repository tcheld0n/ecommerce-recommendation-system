from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import httpx
import os
import uuid

from core.config import settings
from core.database import get_db, engine, Base
from models.payment import Payment, PaymentMethod
from schemas.payment import (
    PaymentCreate, PaymentResponse, PaymentUpdate, 
    PaymentMethodCreate, PaymentMethodResponse,
    PaymentIntentCreate, PaymentIntentResponse
)
from services.payment_service import PaymentService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Payment Service",
    description="Serviço de processamento de pagamentos",
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

# Initialize services
payment_service = PaymentService()

# HTTP client for external service calls
http_client = httpx.AsyncClient()

async def get_current_user_id(token: str) -> int:
    """Get current user ID from auth service"""
    try:
        response = await http_client.post(
            f"{settings.AUTH_SERVICE_URL}/verify-token",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            return data["user"]["id"]
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")

async def verify_order_exists(order_id: int) -> dict:
    """Verify order exists in orders service"""
    try:
        response = await http_client.get(f"{settings.ORDERS_SERVICE_URL}/orders/{order_id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=404, detail="Order not found")
    except Exception:
        raise HTTPException(status_code=404, detail="Order not found")

@app.get("/")
async def root():
    return {"message": "Payment Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/payment-intents", response_model=PaymentIntentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_intent(
    payment_intent: PaymentIntentCreate,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Create a payment intent for an order"""
    user_id = 1  # This should be extracted from JWT token
    
    # Verify order exists and belongs to user
    order = await verify_order_exists(payment_intent.order_id)
    if order["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if order is in correct status for payment
    if order["status"] not in ["pending", "payment_required"]:
        raise HTTPException(status_code=400, detail="Order is not ready for payment")
    
    # Create payment intent
    payment_intent_data = payment_service.create_payment_intent(
        db, user_id, payment_intent
    )
    
    return payment_intent_data

@app.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def process_payment(
    payment_data: PaymentCreate,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Process a payment"""
    user_id = 1  # This should be extracted from JWT token
    
    # Verify order exists
    order = await verify_order_exists(payment_data.order_id)
    if order["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Process payment
    payment = payment_service.process_payment(db, user_id, payment_data)
    
    # Update order status if payment is successful
    if payment.status == "completed":
        try:
            await http_client.put(
                f"{settings.ORDERS_SERVICE_URL}/orders/{payment_data.order_id}",
                json={"status": "confirmed"}
            )
        except Exception:
            # Log error but don't fail the payment
            pass
    
    return payment

@app.get("/payments", response_model=List[PaymentResponse])
async def get_user_payments(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Get current user's payments"""
    user_id = 1  # This should be extracted from JWT token
    
    payments = payment_service.get_user_payments(
        db, user_id, skip=skip, limit=limit, status_filter=status_filter
    )
    return payments

@app.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Get a specific payment"""
    user_id = 1  # This should be extracted from JWT token
    
    payment = payment_service.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check if user owns this payment
    if payment.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return payment

@app.post("/payments/{payment_id}/refund")
async def refund_payment(
    payment_id: int,
    amount: Optional[float] = None,
    reason: Optional[str] = None,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Refund a payment"""
    user_id = 1  # This should be extracted from JWT token
    
    payment = payment_service.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check if user owns this payment
    if payment.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if payment can be refunded
    if payment.status != "completed":
        raise HTTPException(status_code=400, detail="Payment cannot be refunded")
    
    # Process refund
    refund = payment_service.refund_payment(db, payment_id, amount, reason)
    
    # Update order status if refund is successful
    if refund.status == "refunded":
        try:
            await http_client.put(
                f"{settings.ORDERS_SERVICE_URL}/orders/{payment.order_id}",
                json={"status": "refunded"}
            )
        except Exception:
            # Log error but don't fail the refund
            pass
    
    return refund

# Payment methods endpoints
@app.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Get current user's payment methods"""
    user_id = 1  # This should be extracted from JWT token
    
    payment_methods = payment_service.get_user_payment_methods(db, user_id)
    return payment_methods

@app.post("/payment-methods", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_method(
    payment_method: PaymentMethodCreate,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Add a new payment method"""
    user_id = 1  # This should be extracted from JWT token
    
    payment_method_data = payment_service.create_payment_method(db, user_id, payment_method)
    return payment_method_data

@app.delete("/payment-methods/{method_id}")
async def delete_payment_method(
    method_id: int,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Delete a payment method"""
    user_id = 1  # This should be extracted from JWT token
    
    success = payment_service.delete_payment_method(db, user_id, method_id)
    if not success:
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    return {"message": "Payment method deleted successfully"}

@app.patch("/payment-methods/{method_id}/set-default")
async def set_default_payment_method(
    method_id: int,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Set a payment method as default"""
    user_id = 1  # This should be extracted from JWT token
    
    success = payment_service.set_default_payment_method(db, user_id, method_id)
    if not success:
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    return {"message": "Default payment method updated successfully"}

# Webhook endpoints for payment providers
@app.post("/webhooks/stripe")
async def stripe_webhook(request: dict):
    """Handle Stripe webhooks"""
    # TODO: Implement Stripe webhook handling
    return {"status": "received"}

@app.post("/webhooks/paypal")
async def paypal_webhook(request: dict):
    """Handle PayPal webhooks"""
    # TODO: Implement PayPal webhook handling
    return {"status": "received"}

# Admin endpoints
@app.get("/admin/payments", response_model=List[PaymentResponse])
async def get_all_payments(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Get all payments (admin only)"""
    user_id = 1  # This should be extracted from JWT token
    
    # TODO: Verify admin permissions
    payments = payment_service.get_payments(
        db, skip=skip, limit=limit, status_filter=status_filter
    )
    return payments

@app.get("/admin/payments/stats")
async def get_payment_stats(
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Get payment statistics (admin only)"""
    user_id = 1  # This should be extracted from JWT token
    
    # TODO: Verify admin permissions
    stats = payment_service.get_payment_stats(db)
    return stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
