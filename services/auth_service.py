from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_token
from repositories.user_repository import UserRepository
from schemas.user import UserCreate, UserLogin, Token
from models.user import User

class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    async def register_user(self, user_data: UserCreate) -> Tuple[User, Token]:
        """Register a new user."""
        # Check if user already exists
        existing_user = self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user_dict = user_data.dict()
        user_dict["password_hash"] = get_password_hash(user_data.password)
        del user_dict["password"]
        
        user = self.user_repo.create(user_dict)
        
        # Create tokens
        token_data = {"sub": str(user.id)}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        token = Token(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        return user, token

    async def authenticate_user(self, login_data: UserLogin) -> Tuple[User, Token]:
        """Authenticate user and return tokens."""
        user = self.user_repo.get_by_email(login_data.email)
        
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Create tokens
        token_data = {"sub": str(user.id)}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        token = Token(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        return user, token

    async def refresh_access_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token."""
        try:
            payload = verify_token(refresh_token, "refresh")
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            user = self.user_repo.get_by_id(user_id)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            # Create new tokens
            token_data = {"sub": str(user.id)}
            access_token = create_access_token(token_data)
            new_refresh_token = create_refresh_token(token_data)
            
            return Token(
                access_token=access_token,
                refresh_token=new_refresh_token
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.user_repo.get_by_id(user_id)

    async def update_user(self, user_id: str, update_data: dict) -> Optional[User]:
        """Update user information."""
        return self.user_repo.update(user_id, update_data)
