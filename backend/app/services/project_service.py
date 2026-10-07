from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import Project, Task, User, UserRole
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.schemas.task import TaskCreate, TaskUpdate


def get_projects_for_user(db: Session, current_user: User) -> List[Project]:
    """Retrieve projects accessible by the user based on role."""
    if current_user.role == UserRole.ADMIN:
        return db.query(Project).all()
    elif current_user.role == UserRole.MANAGER:
        return db.query(Project).filter(Project.manager_id == current_user.id).all()
    elif current_user.role == UserRole.AGENT:
        # Agent may see projects that contain their assigned tasks
        task_project_ids = [
            t.project_id for t in db.query(Task.project_id).filter(Task.assignee_id == current_user.id).distinct()
        ]
        return db.query(Project).filter(Project.id.in_(task_project_ids)).all()
    return []


def get_tasks_for_user(db: Session, current_user: User, project_id: Optional[int] = None) -> List[Task]:
    """Retrieve tasks accessible by the user based on role."""
    query = db.query(Task)
    if project_id:
        query = query.filter(Task.project_id == project_id)

    if current_user.role == UserRole.ADMIN:
        return query.all()
    elif current_user.role == UserRole.MANAGER:
        # Only tasks in projects managed by current user
        managed_project_ids = [
            p.id for p in db.query(Project.id).filter(Project.manager_id == current_user.id).all()
        ]
        return query.filter(Task.project_id.in_(managed_project_ids)).all()
    elif current_user.role == UserRole.AGENT:
        # Strictly only tasks assigned to this agent
        return query.filter(Task.assignee_id == current_user.id).all()
    return []


def create_project(db: Session, project_in: ProjectCreate) -> Project:
    """Create a new project."""
    project = Project(
        name=project_in.name,
        client_name=project_in.client_name,
        description=project_in.description,
        manager_id=project_in.manager_id,
        deadline=project_in.deadline,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def create_task(db: Session, task_in: TaskCreate) -> Task:
    """Create a new task."""
    task = Task(
        project_id=task_in.project_id,
        title=task_in.title,
        description=task_in.description,
        assignee_id=task_in.assignee_id,
        deadline=task_in.deadline,
        estimated_hours=task_in.estimated_hours,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
