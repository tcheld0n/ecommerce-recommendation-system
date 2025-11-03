"""
Recommendation Service - Sistema de Recomendações
Serviço simples e funcional para recomendar livros
"""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime

import redis.asyncio as redis
import httpx
import time

from core.config import settings
from core.database import get_db, engine, Base
from core.utils import get_current_user_id
from core.logging import setup_logging, log_request, log_response, log_error

logger = setup_logging("recommendation-service")

# Criar tabelas do banco
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Recommendation Service",
    description="Serviço de recomendações de livros",
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

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Redis client (async)
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

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

# Dependency: obter user_id do token
async def get_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """Obter user_id do token JWT"""
    return await get_current_user_id(token)

# Endpoints básicos
@app.get("/")
async def root():
    return {"message": "Recommendation Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Recomendações
@app.get("/recommendations")
async def get_recommendations(
    limit: int = 10,
    user_id: Optional[int] = None,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    debug: bool = False,
):
    """Obter recomendações para o usuário.

    Implementação temporária:
    - Tenta extrair user_id do token (se falhar, segue anônimo)
    - Enquanto o modelo de ML não estiver integrado aqui, faz fallback para livros populares do Catalog Service
    - Retorna no formato { recommendations: [...], user_id }
    """
    if user_id is None and token:
        try:
            user_id = await get_user_id(token)
        except Exception as e:
            logger.warning(f"Falha ao obter user_id do token: {e}")
            user_id = None

    logger.info(f"Obtendo recomendações | user_id={user_id} | limit={limit}")

    # Heurística simples baseada em interações (se existir):
    # - Usa o livro mais recente que o usuário interagiu para puxar recomendações por categoria
    # - Caso contrário, fallback para populares
    personalization_used = False
    source = "fallback_popular"
    recs: List[dict] = []
    try:
        catalog_url = settings.CATALOG_SERVICE_URL
        if not catalog_url:
            raise RuntimeError("CATALOG_SERVICE_URL não configurado")

        last_book_id = None
        if user_id:
            try:
                key = f"user:{user_id}:recent_books"
                # Pegar o último (maior score = timestamp mais recente)
                zs = await redis_client.zrevrange(key, 0, 0)
                if zs:
                    last_book_id = zs[0]
                    logger.info(f"Personalização por interação | user_id={user_id} | last_book_id={last_book_id}")
            except Exception as e:
                logger.warning(f"Falha ao acessar Redis para interações | error={e}")

        async with httpx.AsyncClient(timeout=10.0) as client:
            books: List[dict] = []
            if last_book_id:
                # Buscar categoria do último livro interagido e recomendar da mesma categoria
                try:
                    resp_book = await client.get(f"{catalog_url}/books/{last_book_id}")
                    if resp_book.status_code == 200:
                        base_book = resp_book.json()
                        category_id = base_book.get("category_id")
                        if category_id:
                            personalization_used = True
                            source = "recent_interaction_category"
                            resp_cat = await client.get(
                                f"{catalog_url}/categories/{category_id}/books",
                                params={"limit": max(limit + 1, 2)}
                            )
                            resp_cat.raise_for_status()
                            books = resp_cat.json() or []
                            # evitar recomendar o mesmo livro
                            books = [b for b in books if b.get("id") != last_book_id][:limit]
                except Exception as e:
                    logger.warning(f"Falha ao personalizar por interação | error={e}")

            if not books:
                # Fallback para populares
                async def map_books(lst: List[dict]):
                    out: List[dict] = []
                    for b in lst:
                        out.append({
                            "book_id": b.get("id"),
                            "score": 0.0,
                            "book": {
                                "id": b.get("id"),
                                "isbn": b.get("isbn"),
                                "title": b.get("title"),
                                "author": b.get("author"),
                                "publisher": b.get("publisher"),
                                "published_year": b.get("published_year"),
                                "description": b.get("description"),
                                "price": b.get("price"),
                                "stock_quantity": b.get("stock_quantity"),
                                "cover_image_url": b.get("cover_image_url"),
                                "average_rating": b.get("average_rating", 0),
                                "total_reviews": b.get("total_reviews", 0),
                                "category_id": b.get("category_id"),
                                "created_at": b.get("created_at"),
                                "updated_at": b.get("updated_at"),
                            }
                        })
                    return out

                resp = await client.get(f"{catalog_url}/books/popular", params={"limit": limit})
                resp.raise_for_status()
                books = resp.json() or []
                recs = await map_books(books)
            else:
                # Mapear livros personalizados
                for b in books:
                    recs.append({
                        "book_id": b.get("id"),
                        "score": 0.0,
                        "book": b,
                    })
    except Exception as e:
        logger.error(f"Falha ao obter fallback de populares do Catalog Service: {e}")

    payload = {
        "user_id": user_id,
        "recommendations": recs,
        "message": "OK" if recs else "Sem recomendações",
        "personalization_used": personalization_used,
        "source": source,
    }
    if debug:
        payload["debug"] = {
            "recent_book_id": last_book_id,
        }
    return payload

@app.post("/interactions")
async def record_interaction(interaction_data: dict, request: Request, db: Session = Depends(get_db)):
    """Registrar interação do usuário (VIEW, ADD_TO_CART, PURCHASE, etc.)
    Persiste em Redis para personalização simples posterior.
    Espera payload: { book_id: str, interaction_type: str }
    """
    interaction_type = (interaction_data.get("interaction_type") or interaction_data.get("type") or "").upper()
    book_id = interaction_data.get("book_id")
    now = int(time.time())

    # Extrair user_id do Authorization header, se houver
    user_id = None
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]
            user_id = await get_current_user_id(token)
    except Exception as e:
        logger.warning(f"Falha ao obter user_id no registro de interação: {e}")

    logger.info(f"Registrando interação | user_id={user_id} | book_id={book_id} | type={interaction_type}")

    if user_id and book_id:
        try:
            # Contadores por tipo
            counts_key = f"user:{user_id}:interaction_counts"
            await redis_client.hincrby(counts_key, interaction_type or "UNKNOWN", 1)

            # Últimos livros interagidos (sorted set por timestamp)
            recent_key = f"user:{user_id}:recent_books"
            await redis_client.zadd(recent_key, {book_id: now})
            # manter tamanho máximo
            await redis_client.zremrangebyrank(recent_key, 0, -101)  # mantém os 100 mais recentes
        except Exception as e:
            logger.warning(f"Falha ao gravar interação no Redis | error={e}")

    return {"message": "Interação registrada", "user_id": user_id, "book_id": book_id, "type": interaction_type}

@app.get("/books/{book_id}/similar")
async def get_similar_books(book_id: str, limit: int = 10):
    """Obter livros "similares" ao informado.

    Implementação inicial (fallback sem ML):
    - Busca o livro no Catalog Service para descobrir a categoria
    - Retorna outros livros da mesma categoria (excluindo o próprio), limitando ao parâmetro
    - Mapeia para o formato de Recommendation usado no frontend
    """
    try:
        catalog_url = settings.CATALOG_SERVICE_URL
        if not catalog_url:
            raise RuntimeError("CATALOG_SERVICE_URL não configurado")

        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1) Obter o livro base
            resp_book = await client.get(f"{catalog_url}/books/{book_id}")
            book = None
            if resp_book.status_code == 404:
                logger.warning(f"Livro base não encontrado | book_id={book_id} | retornando fallback")
            else:
                resp_book.raise_for_status()
                book = resp_book.json()

            category_id = book.get("category_id") if book else None
            if not category_id:
                # Se não possuir categoria, retornar populares como fallback
                resp_popular = await client.get(f"{catalog_url}/books/popular", params={"limit": limit})
                resp_popular.raise_for_status()
                books = resp_popular.json() or []
            else:
                # 2) Buscar livros da mesma categoria (pedimos +1 para poder excluir o próprio)
                resp_cat = await client.get(
                    f"{catalog_url}/categories/{category_id}/books",
                    params={"limit": max(limit + 1, 2)}
                )
                resp_cat.raise_for_status()
                books = resp_cat.json() or []

            # 3) Excluir o próprio livro e limitar
            filtered = [b for b in books if b.get("id") != book_id][:limit]

            # 4) Mapear para Recommendation[]
            recs: List[dict] = []
            for b in filtered:
                recs.append({
                    "book_id": b.get("id"),
                    "score": 0.0,
                    "book": {
                        "id": b.get("id"),
                        "isbn": b.get("isbn"),
                        "title": b.get("title"),
                        "author": b.get("author"),
                        "publisher": b.get("publisher"),
                        "published_year": b.get("published_year"),
                        "description": b.get("description"),
                        "price": b.get("price"),
                        "stock_quantity": b.get("stock_quantity"),
                        "cover_image_url": b.get("cover_image_url"),
                        "average_rating": b.get("average_rating", 0),
                        "total_reviews": b.get("total_reviews", 0),
                        "category_id": b.get("category_id"),
                        "created_at": b.get("created_at"),
                        "updated_at": b.get("updated_at"),
                    }
                })

            return recs

    except HTTPException:
        # Não propagar 404 para o frontend; retornar lista vazia para melhor UX
        logger.warning(f"HTTPException ao obter similares | book_id={book_id} | retornando []")
        return []
    except Exception as e:
        logger.error(f"Falha ao obter similares | book_id={book_id} | error={e}")
        # Fallback vazio em caso de erro inesperado
        return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
