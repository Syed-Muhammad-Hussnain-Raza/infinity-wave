from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.project import ProjectResponse, ProjectDetailResponse, ProjectCreate
from app.services.project_service import (
    get_projects_for_user,
    get_project_detail_for_user,
    create_project,
)
from app.dependencies.auth import get_current_user, require_admin

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve projects accessible by the authenticated user.
    - ADMIN: all projects
    - MANAGER: projects where manager_id == current_user.id
    - AGENT: projects containing at least one task assigned to current_user.id
    """
    return get_projects_for_user(db, current_user)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project_by_id(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve project details and authorized tasks.
    - ADMIN: full project and all tasks
    - MANAGER: only if managing this project, with all project tasks
    - AGENT: only if assigned to tasks in this project, with ONLY their own tasks
    Returns 404 consistently if not found or unauthorized (avoids leaking existence).
    """
    return get_project_detail_for_user(db, project_id, current_user)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_new_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new project (Admin only)."""
    return create_project(db, project_in)
