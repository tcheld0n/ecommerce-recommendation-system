from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class CartItemBase(BaseModel):
    book_id: UUID
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItem(CartItemBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CartItemWithBook(CartItem):
    book: Optional[Dict[str, Any]] = None
    unit_price: Optional[Decimal] = None
    subtotal: Optional[Decimal] = None

class Cart(BaseModel):
    id: UUID
    user_id: UUID
    items: List[CartItemWithBook] = []
    total_items: int = 0
    total_amount: Decimal = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
