"""
Catalog Service - Catálogo de Livros
Serviço simples e funcional para gerenciar catálogo e inventário
"""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import time

from core.config import settings
from core.database import get_db, engine, Base
from core.logging import setup_logging, log_request, log_response, log_error, log_database_operation
from models.book import Book, Category
from schemas.book import BookCreate, BookUpdate, Book as BookSchema, CategoryCreate, Category as CategorySchema

logger = setup_logging("catalog-service")

# Criar tabelas do banco
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Catalog Service",
    description="Serviço de catálogo e inventário de livros",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de logging
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """Middleware para logar todas as requisições"""
    start_time = time.time()
    method = request.method
    path = request.url.path
    
    log_request(logger, method, path, client_ip=request.client.host if request.client else None)
    
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        log_response(logger, method, path, response.status_code, duration_ms)
        return response
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        log_error(logger, e, f"{method} {path}")
        log_response(logger, method, path, 500, duration_ms, error=str(e))
        raise

# Endpoints básicos
@app.get("/")
async def root():
    return {"message": "Catalog Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Livros
# IMPORTANTE: Rotas específicas devem vir ANTES da rota genérica /books/{book_id}
@app.get("/books/popular", response_model=List[BookSchema])
async def get_popular_books(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Obter livros populares (ordenados por rating e reviews)"""
    from sqlalchemy.orm import joinedload
    
    logger.info(f"Obtendo livros populares | limit={limit}")
    
    books = db.query(Book).options(joinedload(Book.category))\
        .order_by(Book.average_rating.desc(), Book.total_reviews.desc())\
        .limit(limit).all()
    
    logger.info(f"Retornados {len(books)} livros populares")
    return books

@app.get("/books/recent", response_model=List[BookSchema])
async def get_recent_books(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Obter livros recentes (ordenados por data de criação)"""
    from sqlalchemy.orm import joinedload
    
    logger.info(f"Obtendo livros recentes | limit={limit}")
    
    books = db.query(Book).options(joinedload(Book.category))\
        .order_by(Book.created_at.desc())\
        .limit(limit).all()
    
    logger.info(f"Retornados {len(books)} livros recentes")
    return books

@app.get("/books", response_model=List[BookSchema])
async def get_books(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    sort_by: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listar livros com filtros opcionais"""
    from uuid import UUID
    from sqlalchemy.orm import joinedload
    from sqlalchemy import and_, or_, desc, asc
    from decimal import Decimal
    
    logger.info(f"Listando livros | skip={skip} | limit={limit} | category_id={category_id} | search={search}")
    
    query = db.query(Book).options(joinedload(Book.category))
    
    # Filtro por categoria
    if category_id:
        try:
            # Tentar converter para UUID
            category_uuid = UUID(category_id)
            query = query.filter(Book.category_id == category_uuid)
        except ValueError:
            # Se não for UUID válido, tentar como slug
            category = db.query(Category).filter(Category.slug == category_id).first()
            if category:
                query = query.filter(Book.category_id == category.id)
    
    # Filtro de busca por texto
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Book.title.ilike(search_term),
                Book.author.ilike(search_term),
                Book.isbn.ilike(search_term),
                Book.publisher.ilike(search_term)
            )
        )
    
    # Filtro de preço
    if min_price is not None:
        query = query.filter(Book.price >= Decimal(str(min_price)))
    
    if max_price is not None:
        query = query.filter(Book.price <= Decimal(str(max_price)))
    
    # Filtro de avaliação
    if min_rating is not None:
        query = query.filter(Book.average_rating >= min_rating)
    
    # Ordenação
    if sort_by == "price_asc":
        query = query.order_by(asc(Book.price))
    elif sort_by == "price_desc":
        query = query.order_by(desc(Book.price))
    elif sort_by == "rating":
        query = query.order_by(desc(Book.average_rating))
    elif sort_by == "newest":
        query = query.order_by(desc(Book.created_at))
    else:  # relevance ou padrão
        query = query.order_by(desc(Book.average_rating), desc(Book.total_reviews))
    
    books = query.offset(skip).limit(limit).all()
    logger.info(f"Retornados {len(books)} livros")
    return books

@app.get("/books/{book_id}", response_model=BookSchema)
async def get_book(book_id: str, db: Session = Depends(get_db)):
    """Obter livro específico"""
    from uuid import UUID
    from sqlalchemy.orm import joinedload
    
    logger.info(f"Obtendo livro | book_id={book_id}")
    
    try:
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de livro inválido")
    
    book = db.query(Book).options(joinedload(Book.category))\
        .filter(Book.id == book_uuid).first()
    if not book:
        logger.warning(f"Livro não encontrado | book_id={book_id}")
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    return book

@app.post("/books", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """Criar novo livro"""
    logger.info(f"Criando livro | title={book.title}")
    
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    log_database_operation(logger, "CREATE", "books", db_book.id, title=book.title)
    
    return db_book

@app.put("/books/{book_id}", response_model=BookSchema)
async def update_book(book_id: str, book: BookUpdate, db: Session = Depends(get_db)):
    """Atualizar livro"""
    from uuid import UUID
    
    logger.info(f"Atualizando livro | book_id={book_id}")
    
    try:
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de livro inválido")
    
    db_book = db.query(Book).filter(Book.id == book_uuid).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    for key, value in book.dict(exclude_unset=True).items():
        setattr(db_book, key, value)
    
    db.commit()
    db.refresh(db_book)
    log_database_operation(logger, "UPDATE", "books", book_uuid)
    return db_book

@app.delete("/books/{book_id}")
async def delete_book(book_id: str, db: Session = Depends(get_db)):
    """Deletar livro"""
    from uuid import UUID
    
    logger.info(f"Deletando livro | book_id={book_id}")
    
    try:
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de livro inválido")
    
    db_book = db.query(Book).filter(Book.id == book_uuid).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    db.delete(db_book)
    db.commit()
    log_database_operation(logger, "DELETE", "books", book_uuid)
    return {"message": "Livro deletado com sucesso"}

@app.get("/books/{book_id}/inventory")
async def get_book_inventory(book_id: str, db: Session = Depends(get_db)):
    """Obter informações de inventário do livro"""
    from uuid import UUID
    
    try:
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de livro inválido")
    
    book = db.query(Book).filter(Book.id == book_uuid).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    return {
        "book_id": book_id,
        "title": book.title,
        "stock_quantity": book.stock_quantity,
        "available": book.stock_quantity > 0
    }

@app.patch("/books/{book_id}/inventory")
async def update_inventory(
    book_id: str,
    quantity_change: int,
    db: Session = Depends(get_db)
):
    from uuid import UUID
    """Atualizar quantidade em estoque"""
    logger.info(f"Atualizando inventário | book_id={book_id} | change={quantity_change}")
    
    try:
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de livro inválido")
    
    book = db.query(Book).filter(Book.id == book_uuid).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    old_quantity = book.stock_quantity
    book.stock_quantity += quantity_change
    if book.stock_quantity < 0:
        book.stock_quantity = 0
    
    db.commit()
    log_database_operation(logger, "UPDATE", "books", book_uuid, 
                         old_quantity=old_quantity, new_quantity=book.stock_quantity)
    return {"message": "Inventário atualizado com sucesso"}

# Categorias
@app.get("/categories", response_model=List[CategorySchema])
async def get_categories(db: Session = Depends(get_db)):
    """Listar todas as categorias"""
    categories = db.query(Category).all()
    return categories

@app.get("/categories/{category_id}/books", response_model=List[BookSchema])
async def get_books_by_category(
    category_id: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Obter livros de uma categoria específica"""
    from uuid import UUID
    from sqlalchemy.orm import joinedload
    
    logger.info(f"Obtendo livros por categoria | category_id={category_id} | skip={skip} | limit={limit}")
    
    # Tentar converter para UUID
    try:
        if isinstance(category_id, str):
            category_uuid = UUID(category_id)
        else:
            category_uuid = category_id
        
        books = db.query(Book).options(joinedload(Book.category))\
            .filter(Book.category_id == category_uuid)\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        logger.info(f"Retornados {len(books)} livros da categoria")
        return books
    except ValueError:
        # Se não conseguir converter, tenta como slug
        logger.info(f"Categoria ID não é UUID válido, tentando buscar por slug")
        category = db.query(Category).filter(Category.slug == category_id).first()
        
        if not category:
            logger.warning(f"Categoria não encontrada | category_id={category_id}")
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
        
        books = db.query(Book).options(joinedload(Book.category))\
            .filter(Book.category_id == category.id)\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        logger.info(f"Retornados {len(books)} livros da categoria {category.name}")
        return books

@app.post("/categories", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Criar nova categoria"""
    logger.info(f"Criando categoria | name={category.name}")
    
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    log_database_operation(logger, "CREATE", "categories", db_category.id, name=category.name)
    
    return db_category

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
