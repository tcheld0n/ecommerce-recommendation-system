from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
import os

from core.config import settings
from core.database import get_db, engine, Base
from models.cart import Cart, CartItem
from schemas.cart import CartResponse, CartItemCreate, CartItemUpdate, CartItemResponse
from services.cart_service import CartService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cart Service",
    description="Serviço de gerenciamento de carrinho de compras volátil",
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
cart_service = CartService()

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

async def verify_book_exists(book_id: int) -> dict:
    """Verify book exists in catalog service"""
    try:
        response = await http_client.get(f"{settings.CATALOG_SERVICE_URL}/books/{book_id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=404, detail="Book not found")
    except Exception:
        raise HTTPException(status_code=404, detail="Book not found")

@app.get("/")
async def root():
    return {"message": "Cart Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/cart", response_model=CartResponse)
async def get_cart(
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Get current user's cart"""
    # For now, we'll use a mock user ID - in production, this would come from JWT
    user_id = 1  # This should be extracted from JWT token
    cart = cart_service.get_user_cart(db, user_id)
    if not cart:
        # Create empty cart if doesn't exist
        cart = cart_service.create_cart(db, user_id)
    return cart

@app.post("/cart/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item: CartItemCreate,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Add item to cart"""
    user_id = 1  # This should be extracted from JWT token
    
    # Verify book exists
    book = await verify_book_exists(item.book_id)
    
    # Check if item already exists in cart
    existing_item = cart_service.get_cart_item(db, user_id, item.book_id)
    if existing_item:
        # Update quantity
        updated_item = cart_service.update_cart_item_quantity(
            db, user_id, item.book_id, existing_item.quantity + item.quantity
        )
        return updated_item
    else:
        # Add new item
        cart_item = cart_service.add_to_cart(db, user_id, item)
        return cart_item

@app.put("/cart/items/{book_id}", response_model=CartItemResponse)
async def update_cart_item(
    book_id: int,
    item_update: CartItemUpdate,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    user_id = 1  # This should be extracted from JWT token
    
    # Verify book exists
    await verify_book_exists(book_id)
    
    cart_item = cart_service.update_cart_item_quantity(
        db, user_id, book_id, item_update.quantity
    )
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    return cart_item

@app.delete("/cart/items/{book_id}")
async def remove_from_cart(
    book_id: int,
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    user_id = 1  # This should be extracted from JWT token
    
    success = cart_service.remove_from_cart(db, user_id, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    return {"message": "Item removed from cart successfully"}

@app.delete("/cart")
async def clear_cart(
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Clear entire cart"""
    user_id = 1  # This should be extracted from JWT token
    
    success = cart_service.clear_cart(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cart not found")
    return {"message": "Cart cleared successfully"}

@app.get("/cart/summary")
async def get_cart_summary(
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Get cart summary with totals"""
    user_id = 1  # This should be extracted from JWT token
    
    cart = cart_service.get_user_cart(db, user_id)
    if not cart:
        return {
            "total_items": 0,
            "total_price": 0.0,
            "items": []
        }
    
    # Calculate totals
    total_items = sum(item.quantity for item in cart.items)
    total_price = sum(item.quantity * item.price for item in cart.items)
    
    return {
        "total_items": total_items,
        "total_price": total_price,
        "items": [
            {
                "book_id": item.book_id,
                "title": item.title,
                "quantity": item.quantity,
                "price": item.price,
                "subtotal": item.quantity * item.price
            }
            for item in cart.items
        ]
    }

@app.post("/cart/validate")
async def validate_cart(
    token: str = Depends(lambda: None),  # Will be handled by middleware
    db: Session = Depends(get_db)
):
    """Validate cart items (check availability, prices, etc.)"""
    user_id = 1  # This should be extracted from JWT token
    
    cart = cart_service.get_user_cart(db, user_id)
    if not cart or not cart.items:
        return {"valid": True, "message": "Cart is empty"}
    
    validation_results = []
    all_valid = True
    
    for item in cart.items:
        try:
            # Check book availability
            book_response = await http_client.get(
                f"{settings.CATALOG_SERVICE_URL}/books/{item.book_id}/inventory"
            )
            if book_response.status_code == 200:
                book_data = book_response.json()
                if book_data["stock_quantity"] < item.quantity:
                    validation_results.append({
                        "book_id": item.book_id,
                        "title": item.title,
                        "error": f"Only {book_data['stock_quantity']} items available",
                        "available_quantity": book_data["stock_quantity"]
                    })
                    all_valid = False
                elif book_data["stock_quantity"] == 0:
                    validation_results.append({
                        "book_id": item.book_id,
                        "title": item.title,
                        "error": "Item out of stock",
                        "available_quantity": 0
                    })
                    all_valid = False
            else:
                validation_results.append({
                    "book_id": item.book_id,
                    "title": item.title,
                    "error": "Book not found",
                    "available_quantity": 0
                })
                all_valid = False
        except Exception:
            validation_results.append({
                "book_id": item.book_id,
                "title": item.title,
                "error": "Unable to verify availability",
                "available_quantity": 0
            })
            all_valid = False
    
    return {
        "valid": all_valid,
        "errors": validation_results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
