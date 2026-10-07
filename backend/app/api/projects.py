from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.project import ProjectResponse, ProjectCreate
from app.services.project_service import get_projects_for_user, create_project
from app.dependencies.auth import get_current_user, require_manager_or_admin

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve projects accessible by the authenticated user."""
    return get_projects_for_user(db, current_user)


@router.post("", response_model=ProjectResponse)
def create_new_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """Create a project (Admin or Manager only)."""
    return create_project(db, project_in)
