from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

from app.db.models import UserRole


class UserSimple(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole = UserRole.AGENT
    specialization: Optional[str] = None
    skills: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    specialization: Optional[str] = None
    skills: Optional[str] = None
    role: Optional[UserRole] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    specialization: Optional[str] = None
    skills: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
