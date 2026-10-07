from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserResponse
from app.schemas.task import TaskResponse


class ProjectBase(BaseModel):
    name: str
    client_name: Optional[str] = None
    description: Optional[str] = None
    manager_id: Optional[int] = None
    deadline: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    client_name: Optional[str] = None
    description: Optional[str] = None
    manager_id: Optional[int] = None
    deadline: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    manager: Optional[UserResponse] = None
    tasks: List[TaskResponse] = []

    model_config = ConfigDict(from_attributes=True)
