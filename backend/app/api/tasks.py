from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User, UserRole, Task, Project
from app.schemas.task import TaskResponse, TaskCreate, MyTaskResponse
from app.services.project_service import (
    get_tasks_for_user,
    get_my_tasks_for_user,
    create_task,
)
from app.dependencies.auth import get_current_user, require_admin

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/my", response_model=List[MyTaskResponse])
def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve tasks assigned strictly to the authenticated user (focused view for AGENTs)."""
    return get_my_tasks_for_user(db, current_user)


@router.get("", response_model=List[TaskResponse])
def list_tasks(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve tasks accessible by the authenticated user.
    - ADMIN: all tasks
    - MANAGER: tasks in projects managed by current_user.id
    - AGENT: tasks assigned to current_user.id
    """
    return get_tasks_for_user(db, current_user, project_id=project_id)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a single task if authorized.
    - ADMIN: allowed
    - MANAGER: allowed only if project is managed by current_user.id
    - AGENT: allowed only if task is assigned to current_user.id
    Returns 404 consistently if unauthorized or non-existent (avoids leaking existence).
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if current_user.role == UserRole.ADMIN:
        return task
    elif current_user.role == UserRole.MANAGER:
        project = db.query(Project).filter(Project.id == task.project_id).first()
        if not project or project.manager_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task
    elif current_user.role == UserRole.AGENT:
        if task.assignee_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_new_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new task (Admin only)."""
    return create_task(db, task_in)
