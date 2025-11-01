from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models.user import User
from repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()

    def get_admin_users(self) -> List[User]:
        return self.db.query(User).filter(User.is_admin == True).all()

    def search_users(self, query: str, skip: int = 0, limit: int = 100) -> List[User]:
        return (
            self.db.query(User)
            .filter(
                and_(
                    User.is_active == True,
                    or_(
                        User.full_name.ilike(f"%{query}%"),
                        User.email.ilike(f"%{query}%")
                    )
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
