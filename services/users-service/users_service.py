from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from core.config import settings
from core.database import get_db, engine, Base
from models.user import User
from schemas.user import UserResponse, UserUpdate, AddressCreate, AddressResponse, AddressUpdate
from services.auth_service import AuthService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Users Service",
    description="Serviço de gerenciamento de usuários, perfis e endereços",
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
auth_service = AuthService()

@app.get("/")
async def root():
    return {"message": "Users Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# User profile endpoints
@app.get("/users/me", response_model=UserResponse)
async def get_current_user(current_user: User = Depends(auth_service.get_current_user)):
    """Get current user profile"""
    return current_user

@app.put("/users/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    updated_user = auth_service.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.delete("/users/me")
async def delete_current_user(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user account"""
    success = auth_service.delete_user(db, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User account deleted successfully"}

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (admin only or own profile)"""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user = auth_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Address endpoints
@app.get("/users/me/addresses", response_model=List[AddressResponse])
async def get_user_addresses(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's addresses"""
    return auth_service.get_user_addresses(db, current_user.id)

@app.post("/users/me/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_user_address(
    address: AddressCreate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new address for current user"""
    return auth_service.create_user_address(db, current_user.id, address)

@app.get("/users/me/addresses/{address_id}", response_model=AddressResponse)
async def get_user_address(
    address_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific address for current user"""
    address = auth_service.get_user_address(db, current_user.id, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

@app.put("/users/me/addresses/{address_id}", response_model=AddressResponse)
async def update_user_address(
    address_id: int,
    address_update: AddressUpdate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific address for current user"""
    address = auth_service.update_user_address(db, current_user.id, address_id, address_update)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

@app.delete("/users/me/addresses/{address_id}")
async def delete_user_address(
    address_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific address for current user"""
    success = auth_service.delete_user_address(db, current_user.id, address_id)
    if not success:
        raise HTTPException(status_code=404, detail="Address not found")
    return {"message": "Address deleted successfully"}

@app.patch("/users/me/addresses/{address_id}/set-default")
async def set_default_address(
    address_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Set an address as default for current user"""
    success = auth_service.set_default_address(db, current_user.id, address_id)
    if not success:
        raise HTTPException(status_code=404, detail="Address not found")
    return {"message": "Default address updated successfully"}

# Admin endpoints
@app.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return auth_service.get_users(db, skip=skip, limit=limit)

@app.patch("/admin/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Activate/deactivate user (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    success = auth_service.toggle_user_status(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User status updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
