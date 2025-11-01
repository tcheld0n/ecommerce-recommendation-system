"""
Auth Service - Serviço de autenticação centralizado
Extrai a lógica de negócio do auth-service principal para reutilização
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi import HTTPException, status

from core.config import settings
from core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token
)
from models.user import User
from repositories.user_repository import UserRepository
from schemas.user import UserCreate, UserLogin, Token, UserUpdate


class AuthService:
    """
    Serviço centralizado de autenticação
    Implementa a lógica de negócio para registro, login, refresh de tokens
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
    
    async def register_user(self, user_data: UserCreate) -> Tuple[User, Token]:
        """
        Registrar novo usuário
        
        Args:
            user_data: Dados do novo usuário
            
        Returns:
            Tupla contendo o usuário criado e os tokens
            
        Raises:
            HTTPException: Se o email já está registrado
        """
        # Verificar se email já existe
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já registrado"
            )
        
        # Criar usuário
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            full_name=user_data.full_name,
            reading_preferences=user_data.reading_preferences or {}
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        # Gerar tokens
        tokens = self._generate_tokens(db_user)
        
        return db_user, tokens
    
    async def authenticate_user(self, login_data: UserLogin) -> Tuple[User, Token]:
        """
        Autenticar usuário com email e senha
        
        Args:
            login_data: Email e senha
            
        Returns:
            Tupla contendo o usuário autenticado e os tokens
            
        Raises:
            HTTPException: Se credenciais inválidas ou usuário inativo
        """
        user = self.user_repository.get_by_email(login_data.email)
        
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário inativo"
            )
        
        tokens = self._generate_tokens(user)
        return user, tokens
    
    async def refresh_access_token(self, refresh_token_str: str) -> Token:
        """
        Renovar token de acesso usando refresh token
        
        Args:
            refresh_token_str: Refresh token válido
            
        Returns:
            Novos tokens de acesso e refresh
            
        Raises:
            HTTPException: Se refresh token inválido, expirado ou usuário não encontrado
        """
        # Verificar e decodificar refresh token
        try:
            payload = verify_token(refresh_token_str, token_type="refresh")
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido ou expirado"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # Buscar usuário
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário inativo"
            )
        
        # Gerar novos tokens
        tokens = self._generate_tokens(user)
        return tokens
    
    async def update_user(self, user_id: str, user_data: dict) -> Optional[User]:
        """
        Atualizar informações do usuário
        
        Args:
            user_id: ID do usuário
            user_data: Dados a atualizar (dicionário)
            
        Returns:
            Usuário atualizado ou None se não encontrado
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        # Atualizar apenas campos que foram enviados
        for field, value in user_data.items():
            if value is not None and hasattr(user, field):
                setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def _generate_tokens(self, user: User) -> Token:
        """
        Gerar novos tokens de acesso e refresh para um usuário
        
        Args:
            user: Objeto User
            
        Returns:
            Token contendo access_token, refresh_token e tipo
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
