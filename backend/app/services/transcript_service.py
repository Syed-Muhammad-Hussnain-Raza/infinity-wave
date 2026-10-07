"""Transcript processing service.
Orchestrates AI extraction, Pydantic & database validation,
and atomic persistence of Projects and Tasks.
"""
import threading
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import User, UserRole, Project, Task, Transcript
from app.schemas.transcript import AIExtractedOutput
from app.services.ai_service import ai_service
from app.services.project_service import parse_and_validate_date

# Simple in-memory lock to prevent accidental duplicate submission races
_submission_lock = threading.Lock()


def validate_ai_output_against_db(db: Session, extracted_data: AIExtractedOutput) -> None:
    """Validate all business rules against database before any database modifications:
    - Project: manager exists, role == MANAGER, valid deadline
    - Task: assignee exists, role == AGENT, estimated_hours > 0, task deadline <= project deadline
    If any check fails, raises HTTPException with helpful details.
    """
    all_users = db.query(User).all()
    user_map = {u.id: u for u in all_users}

    for project in extracted_data.projects:
        # Check manager
        manager = user_map.get(project.manager_id)
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Manager ID {project.manager_id} for project '{project.name}' not found in team directory.",
            )
        if manager.role != UserRole.MANAGER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {manager.name} (ID: {manager.id}) assigned as manager for '{project.name}' is not a MANAGER (role: {manager.role.value}).",
            )

        # Validate project deadline
        project_deadline_date = parse_and_validate_date(project.deadline)
        if not project_deadline_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project '{project.name}' must have a valid deadline.",
            )

        # Validate tasks
        if not project.tasks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project '{project.name}' must contain at least one task.",
            )

        for task in project.tasks:
            # Check assignee
            assignee = user_map.get(task.assignee_id)
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Assignee ID {task.assignee_id} for task '{task.title}' not found in team directory.",
                )
            if assignee.role != UserRole.AGENT:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User {assignee.name} (ID: {assignee.id}) assigned to task '{task.title}' is not an AGENT (role: {assignee.role.value}).",
                )

            # Check estimated hours
            if task.estimated_hours <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Task '{task.title}' estimated hours must be greater than 0.",
                )

            # Validate task deadline
            task_deadline_date = parse_and_validate_date(task.deadline)
            if not task_deadline_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Task '{task.title}' must have a valid deadline.",
                )

            # Verify task deadline is not after project deadline
            if task_deadline_date > project_deadline_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Task '{task.title}' deadline ({task_deadline_date}) cannot be after project '{project.name}' deadline ({project_deadline_date}).",
                )


def process_and_save_transcript(
    db: Session,
    raw_transcript: str,
    current_user: User,
) -> Dict[str, Any]:
    """Execute complete end-to-end pipeline:
    1. Check directory users (without sensitive data)
    2. Extract structured data with Gemini AI (fallback to Groq if transient failure)
    3. Validate Pydantic & database constraints
    4. Save in single atomic transaction (or rollback completely)
    """
    if not raw_transcript or not raw_transcript.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcript cannot be empty.",
        )

    # 1. Fetch team directory (sanitize: NO passwords or secrets)
    users = db.query(User).all()
    user_directory = [
        {
            "id": u.id,
            "name": u.name,
            "role": u.role.value,
            "specialization": u.specialization,
            "skills": u.skills,
        }
        for u in users
    ]

    # Acquire lock for thread-safe processing
    acquired = _submission_lock.acquire(blocking=False)
    if not acquired:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Another transcript is currently being processed. Please wait a moment.",
        )

    try:
        # 2. Call AI service for extraction (Primary Gemini, Fallback Groq)
        extracted_data, provider_name = ai_service.parse_meeting_transcript(raw_transcript, user_directory)

        # 3. Validate extracted data against business & DB rules
        validate_ai_output_against_db(db, extracted_data)

        # 4. Atomic database transaction
        created_projects: List[Project] = []
        total_tasks = 0

        try:
            transcript_record = Transcript(
                raw_text=raw_transcript.strip(),
                parsed_data=extracted_data.model_dump_json(),
                created_by_id=current_user.id,
            )
            db.add(transcript_record)

            for p_in in extracted_data.projects:
                project = Project(
                    name=p_in.name.strip(),
                    client_name=p_in.client_name.strip(),
                    description=p_in.description.strip() if p_in.description else None,
                    manager_id=p_in.manager_id,
                    deadline=p_in.deadline.strip(),
                )
                db.add(project)
                db.flush()  # Generate project.id

                for t_in in p_in.tasks:
                    task = Task(
                        project_id=project.id,
                        title=t_in.title.strip(),
                        description=t_in.description.strip() if t_in.description else None,
                        assignee_id=t_in.assignee_id,
                        deadline=t_in.deadline.strip(),
                        estimated_hours=t_in.estimated_hours,
                    )
                    db.add(task)
                    total_tasks += 1

                created_projects.append(project)

            db.commit()

        except Exception as e:
            db.rollback()
            raise e

        # Format success response
        summary_projects = [
            {
                "id": p.id,
                "name": p.name,
                "client_name": p.client_name,
                "deadline": p.deadline,
                "task_count": len(p.tasks),
            }
            for p in created_projects
        ]

        return {
            "message": "Transcript processed successfully",
            "ai_provider": provider_name,
            "projects_created": len(created_projects),
            "tasks_created": total_tasks,
            "projects": summary_projects,
        }

    finally:
        _submission_lock.release()
