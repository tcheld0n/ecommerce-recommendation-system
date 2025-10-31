"""
Auth Service - Autenticação e Autorização
Serviço simples e funcional para gerenciar autenticação de usuários
"""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import time

from core.config import settings
from core.database import get_db, engine, Base
from core.security import create_access_token, create_refresh_token, verify_password, get_password_hash
from core.logging import setup_logging, log_request, log_response, log_error, log_database_operation
from models.user import User
from schemas.user import UserCreate, User as UserSchema, Token

logger = setup_logging("auth-service")

# Criar tabelas do banco
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Auth Service",
    description="Serviço de autenticação e autorização",
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
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Obter usuário atual do token JWT"""
    from jose import JWTError, jwt
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# Endpoints básicos
@app.get("/")
async def root():
    return {"message": "Auth Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Autenticação
@app.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registrar novo usuário"""
    logger.info(f"Registro de usuário | email={user_data.email}")
    
    # Verificar se email já existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logger.warning(f"Email já registrado | email={user_data.email}")
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    # Criar usuário
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    log_database_operation(logger, "CREATE", "users", db_user.id, email=user_data.email)
    
    # Gerar tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_user.email}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": db_user.email})
    
    logger.info(f"Usuário criado | user_id={db_user.id} | email={user_data.email}")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Fazer login e obter token"""
    logger.info(f"Tentativa de login | email={form_data.username}")
    
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        logger.warning(f"Login falhou | email={form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    logger.info(f"Login bem-sucedido | user_id={user.id} | email={user.email}")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Obter informações do usuário atual"""
    logger.info(f"Obtendo informações do usuário | user_id={current_user.id}")
    return current_user

@app.post("/refresh-token", response_model=Token)
@app.post("/refresh", response_model=Token)  # Endpoint alternativo para compatibilidade
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    """Renovar token de acesso usando refresh token"""
    from pydantic import BaseModel
    from jose import JWTError, jwt
    
    class RefreshTokenRequest(BaseModel):
        refresh_token: str
    
    try:
        body = await request.json()
        refresh_token_data = RefreshTokenRequest(**body)
    except Exception as e:
        logger.error(f"Erro ao parsear body do refresh token | error={str(e)}")
        raise HTTPException(status_code=400, detail="Refresh token é obrigatório")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar refresh token
        payload = jwt.decode(refresh_token_data.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError as e:
        logger.warning(f"Erro ao decodificar refresh token | error={str(e)}")
        raise credentials_exception
    
    # Buscar usuário
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        logger.warning(f"Usuário não encontrado para refresh token | email={email}")
        raise credentials_exception
    
    logger.info(f"Renovando token | user_id={user.id} | email={user.email}")
    
    # Criar novo access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Criar novo refresh token também
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
