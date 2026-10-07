from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.user import UserSimple
from app.schemas.task import TaskResponse


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, description="Project name is required")
    client_name: str = Field(..., min_length=1, description="Client name is required")
    description: Optional[str] = None
    manager_id: Optional[int] = None
    deadline: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    client_name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    manager_id: Optional[int] = None
    deadline: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    client_name: str
    description: Optional[str] = None
    manager: Optional[UserSimple] = None
    deadline: Optional[str] = None
    task_count: int = 0
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailResponse(ProjectResponse):
    tasks: List[TaskResponse] = []

    model_config = ConfigDict(from_attributes=True)
