"""
Users Service - Gerenciamento de Usuários e Perfis
Serviço simples e funcional para gerenciar perfis de usuários
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
from core.logging import setup_logging, log_request, log_response, log_error, log_database_operation
from models.user import User
from schemas.user import UserUpdate, User as UserSchema

logger = setup_logging("users-service")

# Criar tabelas do banco
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Users Service",
    description="Serviço de gerenciamento de usuários e perfis",
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

# Dependency: obter usuário atual
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Obter usuário atual do token"""
    user_id = await get_current_user_id(token)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Usuário não encontrado | user_id={user_id}")
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

# Endpoints básicos
@app.get("/")
async def root():
    return {"message": "Users Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Perfil do usuário
@app.get("/users/me", response_model=UserSchema)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Obter perfil do usuário atual"""
    logger.info(f"Obtendo perfil | user_id={current_user.id}")
    return current_user

@app.put("/users/me", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar perfil do usuário atual"""
    logger.info(f"Atualizando perfil | user_id={current_user.id}")
    
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    log_database_operation(logger, "UPDATE", "users", current_user.id)
    logger.info(f"Perfil atualizado | user_id={current_user.id}")
    return current_user

@app.delete("/users/me")
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletar conta do usuário atual"""
    logger.info(f"Deletando conta | user_id={current_user.id}")
    db.delete(current_user)
    db.commit()
    log_database_operation(logger, "DELETE", "users", current_user.id)
    return {"message": "Conta deletada com sucesso"}

# Endereços (placeholder simples)
@app.get("/users/me/addresses")
async def get_user_addresses(current_user: User = Depends(get_current_user)):
    """Obter endereços do usuário (não implementado)"""
    return {"message": "Funcionalidade de endereços não implementada", "addresses": []}

@app.post("/users/me/addresses")
async def create_user_address(address: dict, current_user: User = Depends(get_current_user)):
    """Criar endereço (não implementado)"""
    return {"message": "Funcionalidade de endereços não implementada"}

# Admin (simplificado)
@app.get("/admin/users", response_model=List[UserSchema])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar todos os usuários (admin apenas)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
