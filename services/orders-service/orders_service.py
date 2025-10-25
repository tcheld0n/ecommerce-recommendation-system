from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import httpx
import os

from core.config import settings
from core.database import get_db, engine, Base
from models.order import Order, OrderItem
from schemas.order import OrderCreate, OrderResponse, OrderUpdate, OrderItemResponse
from services.order_service import OrderService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Orders Service",
    description="Serviço de orquestração de pedidos e checkout",
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
order_service = OrderService()

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

async def get_cart_data(user_id: int) -> dict:
    """Get cart data from cart service"""
    try:
        response = await http_client.get(f"{settings.CART_SERVICE_URL}/cart/summary")
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=400, detail="Cart is empty")
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to retrieve cart data")

async def validate_cart(user_id: int) -> bool:
    """Validate cart before creating order"""
    try:
        response = await http_client.post(f"{settings.CART_SERVICE_URL}/cart/validate")
        if response.status_code == 200:
            data = response.json()
            return data["valid"]
        return False
    except Exception:
        return False

async def reserve_inventory(order_items: List[dict]) -> bool:
    """Reserve inventory in catalog service"""
    try:
        for item in order_items:
            response = await http_client.patch(
                f"{settings.CATALOG_SERVICE_URL}/books/{item['book_id']}/inventory",
                json={"quantity_change": -item["quantity"]}
            )
            if response.status_code != 200:
                return False
        return True
    except Exception:
        return False

async def release_inventory(order_items: List[dict]) -> bool:
    """Release inventory in catalog service"""
    try:
        for item in order_items:
            response = await http_client.patch(
                f"{settings.CATALOG_SERVICE_URL}/books/{item['book_id']}/inventory",
                json={"quantity_change": item["quantity"]}
            )
            if response.status_code != 200:
                return False
        return True
    except Exception:
        return False

@app.get("/")
async def root():
    return {"message": "Orders Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Create a new order from cart"""
    user_id = 1  # This should be extracted from JWT token
    
    # Validate cart
    if not await validate_cart(user_id):
        raise HTTPException(status_code=400, detail="Cart validation failed")
    
    # Get cart data
    cart_data = await get_cart_data(user_id)
    if not cart_data["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Reserve inventory
    if not await reserve_inventory(cart_data["items"]):
        raise HTTPException(status_code=400, detail="Unable to reserve inventory")
    
    try:
        # Create order
        order = order_service.create_order(db, user_id, order_data, cart_data)
        
        # Clear cart after successful order creation
        await http_client.delete(f"{settings.CART_SERVICE_URL}/cart")
        
        return order
    except Exception as e:
        # Release inventory if order creation fails
        await release_inventory(cart_data["items"])
        raise HTTPException(status_code=500, detail="Order creation failed")

@app.get("/orders", response_model=List[OrderResponse])
async def get_user_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Get current user's orders"""
    user_id = 1  # This should be extracted from JWT token
    
    orders = order_service.get_user_orders(
        db, user_id, skip=skip, limit=limit, status_filter=status_filter
    )
    return orders

@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Get a specific order"""
    user_id = 1  # This should be extracted from JWT token
    
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user owns this order
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return order

@app.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Update order status"""
    user_id = 1  # This should be extracted from JWT token
    
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user owns this order
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Only allow certain status updates
    if order_update.status not in ["cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status update")
    
    updated_order = order_service.update_order(db, order_id, order_update)
    return updated_order

@app.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Cancel an order"""
    user_id = 1  # This should be extracted from JWT token
    
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user owns this order
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if order can be cancelled
    if order.status not in ["pending", "confirmed"]:
        raise HTTPException(status_code=400, detail="Order cannot be cancelled")
    
    # Release inventory
    order_items = [
        {"book_id": item.book_id, "quantity": item.quantity}
        for item in order.items
    ]
    await release_inventory(order_items)
    
    # Update order status
    order_update = OrderUpdate(status="cancelled")
    updated_order = order_service.update_order(db, order_id, order_update)
    
    return {"message": "Order cancelled successfully", "order": updated_order}

@app.get("/orders/{order_id}/items", response_model=List[OrderItemResponse])
async def get_order_items(
    order_id: int,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Get order items"""
    user_id = 1  # This should be extracted from JWT token
    
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user owns this order
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return order.items

@app.post("/orders/{order_id}/track")
async def track_order(
    order_id: int,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Track order status"""
    user_id = 1  # This should be extracted from JWT token
    
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user owns this order
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Return tracking information
    return {
        "order_id": order_id,
        "status": order.status,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "tracking_number": order.tracking_number,
        "estimated_delivery": order.estimated_delivery
    }

# Admin endpoints
@app.get("/admin/orders", response_model=List[OrderResponse])
async def get_all_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Get all orders (admin only)"""
    user_id = 1  # This should be extracted from JWT token
    
    # TODO: Verify admin permissions
    orders = order_service.get_orders(
        db, skip=skip, limit=limit, status_filter=status_filter
    )
    return orders

@app.put("/admin/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status_update: OrderUpdate,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Update order status (admin only)"""
    user_id = 1  # This should be extracted from JWT token
    
    # TODO: Verify admin permissions
    updated_order = order_service.update_order(db, order_id, status_update)
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return updated_order

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
