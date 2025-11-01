from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from models.order import OrderStatus, PaymentStatus

# Importar schema Book para usar em OrderItemWithBook
try:
    from schemas.book import Book as BookSchema
except ImportError:
    # Fallback caso o import falhe
    BookSchema = BaseModel  # Usar BaseModel como placeholder

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
    
    # Usar BookSchema para aceitar objetos ORM diretamente
    # O Pydantic vai automaticamente ler os atributos do objeto Book SQLAlchemy
    book: Optional[BookSchema] = None

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
