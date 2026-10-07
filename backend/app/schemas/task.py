from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.schemas.user import UserSimple


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, description="Task title is required")
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    deadline: Optional[str] = None
    estimated_hours: Optional[float] = Field(None, gt=0, description="Estimated hours must be greater than 0")


class TaskCreate(TaskBase):
    project_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    deadline: Optional[str] = None
    estimated_hours: Optional[float] = Field(None, gt=0)


class TaskResponse(BaseModel):
    id: int
    project_id: int
    project_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    assignee: Optional[UserSimple] = None
    deadline: Optional[str] = None
    estimated_hours: Optional[float] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MyTaskResponse(BaseModel):
    id: int
    project_id: int
    project_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    deadline: Optional[str] = None
    estimated_hours: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
