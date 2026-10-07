from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.db.models import User
from app.core.security import verify_password, hash_password, create_access_token
from app.schemas.user import UserCreate


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Verify user credentials and return the user if valid."""
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_user_token(user: User) -> Dict[str, Any]:
    """Generate JWT access token containing user identity and role."""
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "name": user.name,
    }
    token = create_access_token(token_data)
    return {
        "access_token": token,
        "token_type": "bearer",
    }


def create_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user with hashed password."""
    new_user = User(
        name=user_in.name,
        email=user_in.email.strip().lower(),
        password_hash=hash_password(user_in.password),
        role=user_in.role,
        specialization=user_in.specialization,
        skills=user_in.skills,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
