from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, AliasChoices, field_validator


class AIExtractedTask(BaseModel):
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description or scope")
    assignee_id: int = Field(
        ...,
        description="ID of the assigned AGENT user from the directory",
        validation_alias=AliasChoices("assigneeId", "assignee_id"),
    )
    deadline: str = Field(
        ...,
        description="Deadline in YYYY-MM-DD format",
    )
    estimated_hours: float = Field(
        ...,
        description="Estimated effort in hours",
        validation_alias=AliasChoices("estimatedHours", "estimated_hours"),
    )

    @field_validator("estimated_hours")
    @classmethod
    def validate_hours(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Estimated hours must be greater than 0")
        return v

    model_config = ConfigDict(populate_by_name=True)


class AIExtractedProject(BaseModel):
    name: str = Field(..., description="Project name")
    client_name: str = Field(
        ...,
        description="Client name",
        validation_alias=AliasChoices("clientName", "client_name"),
    )
    description: Optional[str] = Field(None, description="Project description or overview")
    manager_id: int = Field(
        ...,
        description="ID of the project MANAGER user from the directory",
        validation_alias=AliasChoices("managerId", "manager_id"),
    )
    deadline: str = Field(
        ...,
        description="Deadline in YYYY-MM-DD format",
    )
    tasks: List[AIExtractedTask] = Field(
        ...,
        description="List of tasks for this project",
    )

    model_config = ConfigDict(populate_by_name=True)


class AIExtractedOutput(BaseModel):
    projects: List[AIExtractedProject] = Field(
        ...,
        description="List of extracted projects",
    )

    model_config = ConfigDict(populate_by_name=True)


class TranscriptProcessRequest(BaseModel):
    transcript: str = Field(
        ...,
        min_length=1,
        description="Raw meeting transcript text",
        validation_alias=AliasChoices("transcript", "transcript_text"),
    )

    model_config = ConfigDict(populate_by_name=True)


class TranscriptProjectSummary(BaseModel):
    id: int
    name: str
    client_name: str
    deadline: Optional[str] = None
    task_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class TranscriptProcessResponse(BaseModel):
    message: str = "Transcript processed successfully"
    ai_provider: Optional[str] = None
    projects_created: int
    tasks_created: int
    projects: List[TranscriptProjectSummary] = []

    model_config = ConfigDict(from_attributes=True)
