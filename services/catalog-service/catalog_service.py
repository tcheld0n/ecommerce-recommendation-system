from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from core.config import settings
from core.database import get_db, engine, Base
from models.book import Book, Category
from schemas.book import BookCreate, BookUpdate, Book as BookSchema, CategoryCreate, Category as CategorySchema
# BookService removed - implementing logic directly

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

# Services initialized directly in endpoints

@app.get("/")
async def root():
    return {"message": "Catalog Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Books endpoints
@app.get("/books", response_model=List[BookSchema])
async def get_books(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get books with optional filtering"""
    query = db.query(Book)
    
    if category_id:
        query = query.filter(Book.category_id == category_id)
    
    if search:
        query = query.filter(Book.title.ilike(f"%{search}%"))
    
    books = query.offset(skip).limit(limit).all()
    return books

@app.get("/books/{book_id}", response_model=BookSchema)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    """Get a specific book by ID"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/books", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """Create a new book"""
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.put("/books/{book_id}", response_model=BookSchema)
async def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    """Update a book"""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    for key, value in book.dict(exclude_unset=True).items():
        setattr(db_book, key, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book

@app.delete("/books/{book_id}")
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Delete a book"""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted successfully"}

@app.get("/books/{book_id}/inventory")
async def get_book_inventory(book_id: int, db: Session = Depends(get_db)):
    """Get inventory information for a book"""
    book = db.query(Book).filter(Book.id == book_id).first()
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
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    book.stock_quantity += quantity_change
    if book.stock_quantity < 0:
        book.stock_quantity = 0
    
    db.commit()
    return {"message": "Inventory updated successfully"}

# Categories endpoints
@app.get("/categories", response_model=List[CategorySchema])
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    return db.query(Category).all()

@app.post("/categories", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)