from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from core.config import settings
from core.database import get_db, engine, Base
from models.book import Book, Category
from schemas.book import BookCreate, BookUpdate, BookResponse, CategoryCreate, CategoryResponse
from services.book_service import BookService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Catalog Service",
    description="Serviço de catálogo e inventário de livros",
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
book_service = BookService()

@app.get("/")
async def root():
    return {"message": "Catalog Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Books endpoints
@app.get("/books", response_model=List[BookResponse])
async def get_books(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get books with optional filtering"""
    return book_service.get_books(db, skip=skip, limit=limit, category_id=category_id, search=search)

@app.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    """Get a specific book by ID"""
    book = book_service.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """Create a new book"""
    return book_service.create_book(db, book)

@app.put("/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    """Update a book"""
    updated_book = book_service.update_book(db, book_id, book)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book

@app.delete("/books/{book_id}")
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Delete a book"""
    success = book_service.delete_book(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}

@app.get("/books/{book_id}/inventory")
async def get_book_inventory(book_id: int, db: Session = Depends(get_db)):
    """Get inventory information for a book"""
    book = book_service.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {
        "book_id": book_id,
        "title": book.title,
        "stock_quantity": book.stock_quantity,
        "available": book.stock_quantity > 0
    }

@app.patch("/books/{book_id}/inventory")
async def update_inventory(
    book_id: int, 
    quantity_change: int, 
    db: Session = Depends(get_db)
):
    """Update inventory quantity for a book"""
    success = book_service.update_inventory(db, book_id, quantity_change)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Inventory updated successfully"}

# Categories endpoints
@app.get("/categories", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    return book_service.get_categories(db)

@app.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    return book_service.create_category(db, category)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)