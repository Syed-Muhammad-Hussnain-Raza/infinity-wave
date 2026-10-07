from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.task import TaskResponse, TaskCreate
from app.services.project_service import get_tasks_for_user, create_task
from app.dependencies.auth import get_current_user, require_manager_or_admin

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=List[TaskResponse])
def list_tasks(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve tasks accessible by the authenticated user."""
    return get_tasks_for_user(db, current_user, project_id=project_id)


@router.post("", response_model=TaskResponse)
def create_new_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """Create a new task (Admin or Manager only)."""
    return create_task(db, task_in)
