from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[UUID] = None

class Category(CategoryBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class BookTagBase(BaseModel):
    tag: str

class BookTagCreate(BookTagBase):
    pass

class BookTag(BookTagBase):
    id: UUID
    book_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class BookBase(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: str
    published_year: int
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int = 0
    cover_image_url: Optional[str] = None
    category_id: UUID

class BookCreate(BookBase):
    tags: Optional[List[str]] = []

class BookUpdate(BaseModel):
    isbn: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    published_year: Optional[int] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    cover_image_url: Optional[str] = None
    category_id: Optional[UUID] = None
    tags: Optional[List[str]] = None

class Book(BookBase):
    id: UUID
    average_rating: float
    total_reviews: int
    created_at: datetime
    updated_at: datetime
    category: Optional[Category] = None
    tags: Optional[List[BookTag]] = []
    
    class Config:
        from_attributes = True

class BookSearch(BaseModel):
    query: Optional[str] = None
    category_id: Optional[UUID] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    min_rating: Optional[float] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    published_year: Optional[int] = None
    sort_by: Optional[str] = "relevance"  # relevance, price_asc, price_desc, rating, newest
    page: int = 1
    limit: int = 20
