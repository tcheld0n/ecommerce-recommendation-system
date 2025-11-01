from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from models.order import OrderStatus, PaymentStatus

# Schema simples de Book sem relacionamentos circulares
class BookSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    title: str
    author: str
    isbn: str
    price: Decimal
    cover_image_url: Optional[str] = None

class OrderItemBase(BaseModel):
    book_id: UUID
    quantity: int
    unit_price: Decimal

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    subtotal: Decimal
    created_at: datetime

class OrderItemWithBook(OrderItem):
    model_config = ConfigDict(from_attributes=True)
    
    # Usar BookSimple para evitar referências circulares
    book: Optional[BookSimple] = None

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
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    status: OrderStatus
    total_amount: Decimal
    payment_status: PaymentStatus
    tracking_code: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemWithBook] = []

class OrderSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    items_count: int
