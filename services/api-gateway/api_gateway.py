from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional
import httpx
import os

from core.config import settings

app = FastAPI(
    title="E-commerce API Gateway",
    description="API Gateway para orquestração de microsserviços",
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

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# HTTP client for service calls
http_client = httpx.AsyncClient()

# Service URLs
SERVICE_URLS = {
    "catalog": settings.CATALOG_SERVICE_URL,
    "auth": settings.AUTH_SERVICE_URL,
    "users": settings.USERS_SERVICE_URL,
    "cart": settings.CART_SERVICE_URL,
    "orders": settings.ORDERS_SERVICE_URL,
    "payment": settings.PAYMENT_SERVICE_URL,
    "recommendation": settings.RECOMMENDATION_SERVICE_URL,
}

@app.get("/")
async def root():
    return {
        "message": "E-commerce API Gateway",
        "version": "1.0.0",
        "services": list(SERVICE_URLS.keys())
    }

@app.get("/health")
async def health_check():
    """Health check for all services"""
    health_status = {}
    
    for service_name, service_url in SERVICE_URLS.items():
        try:
            response = await http_client.get(f"{service_url}/health", timeout=5.0)
            health_status[service_name] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "url": service_url
            }
        except Exception:
            health_status[service_name] = {
                "status": "unhealthy",
                "url": service_url
            }
    
    return {
        "gateway": "healthy",
        "services": health_status
    }

# Catalog Service Routes
@app.get("/api/v1/books")
async def get_books(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    search: Optional[str] = None
):
    """Get books from catalog service"""
    try:
        response = await http_client.get(
            f"{SERVICE_URLS['catalog']}/books",
            params={"skip": skip, "limit": limit, "category_id": category_id, "search": search}
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Catalog service unavailable")

@app.get("/api/v1/books/{book_id}")
async def get_book(book_id: int):
    """Get specific book from catalog service"""
    try:
        response = await http_client.get(f"{SERVICE_URLS['catalog']}/books/{book_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Book not found")
        return response.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Catalog service unavailable")

# Auth Service Routes
@app.post("/api/v1/auth/register")
async def register(user_data: dict):
    """Register user through auth service"""
    try:
        response = await http_client.post(
            f"{SERVICE_URLS['auth']}/register",
            json=user_data
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Auth service unavailable")

@app.post("/api/v1/auth/login")
async def login(credentials: dict):
    """Login user through auth service"""
    try:
        response = await http_client.post(
            f"{SERVICE_URLS['auth']}/login",
            data=credentials
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Auth service unavailable")

# Users Service Routes
@app.get("/api/v1/users/me")
async def get_current_user(authorization: str = None):
    """Get current user profile"""
    try:
        headers = {"Authorization": authorization} if authorization else {}
        response = await http_client.get(
            f"{SERVICE_URLS['users']}/users/me",
            headers=headers
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Users service unavailable")

# Cart Service Routes
@app.get("/api/v1/cart")
async def get_cart(authorization: str = None):
    """Get user cart"""
    try:
        headers = {"Authorization": authorization} if authorization else {}
        response = await http_client.get(
            f"{SERVICE_URLS['cart']}/cart",
            headers=headers
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Cart service unavailable")

@app.post("/api/v1/cart/items")
async def add_to_cart(item_data: dict, authorization: str = None):
    """Add item to cart"""
    try:
        headers = {"Authorization": authorization} if authorization else {}
        response = await http_client.post(
            f"{SERVICE_URLS['cart']}/cart/items",
            json=item_data,
            headers=headers
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Cart service unavailable")

# Orders Service Routes
@app.post("/api/v1/orders")
async def create_order(order_data: dict, authorization: str = None):
    """Create order"""
    try:
        headers = {"Authorization": authorization} if authorization else {}
        response = await http_client.post(
            f"{SERVICE_URLS['orders']}/orders",
            json=order_data,
            headers=headers
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Orders service unavailable")

@app.get("/api/v1/orders")
async def get_orders(authorization: str = None):
    """Get user orders"""
    try:
        headers = {"Authorization": authorization} if authorization else {}
        response = await http_client.get(
            f"{SERVICE_URLS['orders']}/orders",
            headers=headers
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Orders service unavailable")

# Payment Service Routes
@app.post("/api/v1/payments")
async def process_payment(payment_data: dict, authorization: str = None):
    """Process payment"""
    try:
        headers = {"Authorization": authorization} if authorization else {}
        response = await http_client.post(
            f"{SERVICE_URLS['payment']}/payments",
            json=payment_data,
            headers=headers
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Payment service unavailable")

# Recommendation Service Routes
@app.get("/api/v1/recommendations")
async def get_recommendations(authorization: str = None):
    """Get user recommendations"""
    try:
        headers = {"Authorization": authorization} if authorization else {}
        response = await http_client.get(
            f"{SERVICE_URLS['recommendation']}/recommendations",
            headers=headers
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Recommendation service unavailable")

# Composite endpoints
@app.get("/api/v1/dashboard")
async def get_dashboard(authorization: str = None):
    """Get user dashboard with recommendations and recent orders"""
    try:
        headers = {"Authorization": authorization} if authorization else {}
        
        # Get recommendations
        recommendations_response = await http_client.get(
            f"{SERVICE_URLS['recommendation']}/recommendations",
            headers=headers
        )
        recommendations = recommendations_response.json() if recommendations_response.status_code == 200 else []
        
        # Get recent orders
        orders_response = await http_client.get(
            f"{SERVICE_URLS['orders']}/orders?limit=5",
            headers=headers
        )
        recent_orders = orders_response.json() if orders_response.status_code == 200 else []
        
        # Get trending books
        trending_response = await http_client.get(
            f"{SERVICE_URLS['recommendation']}/trending?limit=5"
        )
        trending_books = trending_response.json() if trending_response.status_code == 200 else []
        
        return {
            "recommendations": recommendations,
            "recent_orders": recent_orders,
            "trending_books": trending_books
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Dashboard service unavailable")

@app.get("/api/v1/checkout/summary")
async def get_checkout_summary(authorization: str = None):
    """Get checkout summary with cart and user info"""
    try:
        headers = {"Authorization": authorization} if authorization else {}
        
        # Get cart summary
        cart_response = await http_client.get(
            f"{SERVICE_URLS['cart']}/cart/summary",
            headers=headers
        )
        cart_summary = cart_response.json() if cart_response.status_code == 200 else {}
        
        # Get user addresses
        addresses_response = await http_client.get(
            f"{SERVICE_URLS['users']}/users/me/addresses",
            headers=headers
        )
        addresses = addresses_response.json() if addresses_response.status_code == 200 else []
        
        # Get payment methods
        payment_methods_response = await http_client.get(
            f"{SERVICE_URLS['payment']}/payment-methods",
            headers=headers
        )
        payment_methods = payment_methods_response.json() if payment_methods_response.status_code == 200 else []
        
        return {
            "cart": cart_summary,
            "addresses": addresses,
            "payment_methods": payment_methods
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Checkout summary service unavailable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
