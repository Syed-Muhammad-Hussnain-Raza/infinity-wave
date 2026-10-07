from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict


class ExtractedTaskSchema(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_name: Optional[str] = None
    deadline: Optional[str] = None
    estimated_hours: Optional[float] = 0.0


class ExtractedProjectSchema(BaseModel):
    name: str
    client_name: Optional[str] = None
    description: Optional[str] = None
    manager_name: Optional[str] = None
    deadline: Optional[str] = None
    tasks: List[ExtractedTaskSchema] = []


class TranscriptInput(BaseModel):
    transcript_text: str


class TranscriptProcessResponse(BaseModel):
    id: Optional[int] = None
    message: str
    projects: List[ExtractedProjectSchema] = []
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
