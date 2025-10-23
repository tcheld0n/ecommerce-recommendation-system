from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from models.order import OrderStatus, PaymentStatus

class OrderItemBase(BaseModel):
    book_id: UUID
    quantity: int
    unit_price: Decimal

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: UUID
    subtotal: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderItemWithBook(OrderItem):
    book: Optional[Dict[str, Any]] = None

class OrderBase(BaseModel):
    shipping_address: Dict[str, Any]
    payment_method: str

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    tracking_code: Optional[str] = None

class Order(OrderBase):
    id: UUID
    user_id: UUID
    status: OrderStatus
    total_amount: Decimal
    payment_status: PaymentStatus
    tracking_code: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemWithBook] = []
    
    class Config:
        from_attributes = True

class OrderSummary(BaseModel):
    id: UUID
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    items_count: int
    
    class Config:
        from_attributes = True
