"""
Recommendation Service - Sistema de Recomendações
Serviço simples e funcional para recomendar livros
"""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
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
    db: Session = Depends(get_db)
):
    """Obter recomendações para o usuário"""
    if user_id is None and token:
        try:
            user_id = await get_user_id(token)
        except:
            pass
    
    logger.info(f"Obtendo recomendações | user_id={user_id} | limit={limit}")
    
    # Implementação simplificada - retorna lista vazia por enquanto
    # Em produção, aqui seria implementada lógica de ML
    return {
        "user_id": user_id,
        "recommendations": [],
        "message": "Sistema de recomendações em desenvolvimento"
    }

@app.post("/interactions")
async def record_interaction(interaction_data: dict, db: Session = Depends(get_db)):
    """Registrar interação do usuário (visualização, compra, etc.)"""
    logger.info(f"Registrando interação | type={interaction_data.get('type')}")
    
    # Implementação simplificada
    return {
        "message": "Interação registrada com sucesso",
        "interaction_id": interaction_data.get("id")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
