from datetime import datetime, date
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import Project, Task, User, UserRole
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectDetailResponse
from app.schemas.task import TaskCreate, TaskResponse


def parse_and_validate_date(date_str: Optional[str]) -> Optional[date]:
    """Parse a date string in common formats (YYYY-MM-DD, '20 October 2026', etc.).
    Returns a date object or raises 400 HTTPException.
    """
    if not date_str or not date_str.strip():
        return None
    cleaned = date_str.strip()
    for fmt in ("%Y-%m-%d", "%d %B %Y", "%d %b %Y", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            pass
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid date format: '{date_str}'. Expected format YYYY-MM-DD or 'DD Month YYYY'",
    )


def get_projects_for_user(db: Session, current_user: User) -> List[Dict[str, Any]]:
    """Retrieve projects accessible by current_user based on role.
    Computes task_count scoped to what the user is authorized to see.
    """
    if current_user.role == UserRole.ADMIN:
        projects = db.query(Project).all()
        result = []
        for p in projects:
            p_dict = {
                "id": p.id,
                "name": p.name,
                "client_name": p.client_name,
                "description": p.description,
                "manager": p.manager,
                "deadline": p.deadline,
                "task_count": len(p.tasks),
                "created_at": p.created_at,
            }
            result.append(p_dict)
        return result

    elif current_user.role == UserRole.MANAGER:
        projects = db.query(Project).filter(Project.manager_id == current_user.id).all()
        result = []
        for p in projects:
            p_dict = {
                "id": p.id,
                "name": p.name,
                "client_name": p.client_name,
                "description": p.description,
                "manager": p.manager,
                "deadline": p.deadline,
                "task_count": len(p.tasks),
                "created_at": p.created_at,
            }
            result.append(p_dict)
        return result

    elif current_user.role == UserRole.AGENT:
        # Return distinct projects for which the agent has at least one assigned task
        projects = (
            db.query(Project)
            .join(Task, Task.project_id == Project.id)
            .filter(Task.assignee_id == current_user.id)
            .distinct()
            .all()
        )
        result = []
        for p in projects:
            # Count only tasks assigned to this agent in this project
            agent_tasks = [t for t in p.tasks if t.assignee_id == current_user.id]
            p_dict = {
                "id": p.id,
                "name": p.name,
                "client_name": p.client_name,
                "description": p.description,
                "manager": p.manager,
                "deadline": p.deadline,
                "task_count": len(agent_tasks),
                "created_at": p.created_at,
            }
            result.append(p_dict)
        return result

    return []


def get_project_detail_for_user(
    db: Session, project_id: int, current_user: User
) -> Dict[str, Any]:
    """Retrieve single project detail if authorized.
    Returns 404 consistently if project does not exist or user is unauthorized
    to prevent leaking project existence.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if current_user.role == UserRole.ADMIN:
        authorized_tasks = project.tasks
    elif current_user.role == UserRole.MANAGER:
        if project.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        authorized_tasks = project.tasks
    elif current_user.role == UserRole.AGENT:
        agent_tasks = [t for t in project.tasks if t.assignee_id == current_user.id]
        if not agent_tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        authorized_tasks = agent_tasks
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return {
        "id": project.id,
        "name": project.name,
        "client_name": project.client_name,
        "description": project.description,
        "manager": project.manager,
        "deadline": project.deadline,
        "task_count": len(authorized_tasks),
        "tasks": authorized_tasks,
        "created_at": project.created_at,
    }


def get_tasks_for_user(
    db: Session, current_user: User, project_id: Optional[int] = None
) -> List[Task]:
    """Retrieve tasks accessible by current_user based on role."""
    if current_user.role == UserRole.ADMIN:
        query = db.query(Task)
        if project_id:
            query = query.filter(Task.project_id == project_id)
        return query.all()

    elif current_user.role == UserRole.MANAGER:
        query = (
            db.query(Task)
            .join(Project, Project.id == Task.project_id)
            .filter(Project.manager_id == current_user.id)
        )
        if project_id:
            query = query.filter(Task.project_id == project_id)
        return query.all()

    elif current_user.role == UserRole.AGENT:
        query = db.query(Task).filter(Task.assignee_id == current_user.id)
        if project_id:
            query = query.filter(Task.project_id == project_id)
        return query.all()

    return []


def get_my_tasks_for_user(db: Session, current_user: User) -> List[Task]:
    """Retrieve tasks assigned strictly to current_user."""
    return db.query(Task).filter(Task.assignee_id == current_user.id).all()


def create_project(db: Session, project_in: ProjectCreate) -> Project:
    """Create a new project with validation.
    - name required
    - client_name required
    - manager_id must reference an existing MANAGER
    - deadline must be a valid date
    """
    if not project_in.name or not project_in.name.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project name is required")
    if not project_in.client_name or not project_in.client_name.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client name is required")

    # Validate manager_id if provided
    if project_in.manager_id is not None:
        manager = db.query(User).filter(User.id == project_in.manager_id).first()
        if not manager:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Manager not found")
        if manager.role != UserRole.MANAGER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {manager.name} is not a MANAGER (role: {manager.role.value})"
            )

    # Validate deadline format
    norm_deadline_str = None
    if project_in.deadline:
        parsed_deadline = parse_and_validate_date(project_in.deadline)
        norm_deadline_str = parsed_deadline.isoformat() if parsed_deadline else None

    project = Project(
        name=project_in.name.strip(),
        client_name=project_in.client_name.strip(),
        description=project_in.description.strip() if project_in.description else None,
        manager_id=project_in.manager_id,
        deadline=norm_deadline_str or project_in.deadline,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def create_task(db: Session, task_in: TaskCreate) -> Task:
    """Create a new task with validation:
    - title required
    - project_id must reference an existing project
    - assignee_id must reference an existing AGENT
    - estimated_hours must be > 0
    - deadline must be valid
    - task deadline should not be after project deadline
    """
    if not task_in.title or not task_in.title.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task title is required")

    # Verify project exists
    project = db.query(Project).filter(Project.id == task_in.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project not found")

    # Verify assignee is an AGENT
    if task_in.assignee_id is not None:
        assignee = db.query(User).filter(User.id == task_in.assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignee not found")
        if assignee.role != UserRole.AGENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {assignee.name} is not an AGENT (role: {assignee.role.value})"
            )

    # Validate estimated_hours
    if task_in.estimated_hours is not None and task_in.estimated_hours <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estimated hours must be greater than 0"
        )

    # Validate deadline
    task_deadline_date = None
    norm_task_deadline_str = None
    if task_in.deadline:
        task_deadline_date = parse_and_validate_date(task_in.deadline)
        norm_task_deadline_str = task_deadline_date.isoformat() if task_deadline_date else None

    # Validate task deadline against project deadline
    if task_deadline_date and project.deadline:
        try:
            project_deadline_date = parse_and_validate_date(project.deadline)
            if project_deadline_date and task_deadline_date > project_deadline_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Task deadline ({task_deadline_date}) cannot be after project deadline ({project_deadline_date})"
                )
        except HTTPException as e:
            if e.status_code == status.HTTP_400_BAD_REQUEST and "cannot be after" in str(e.detail):
                raise e
            # If project deadline wasn't standard, skip date comparison

    task = Task(
        project_id=task_in.project_id,
        title=task_in.title.strip(),
        description=task_in.description.strip() if task_in.description else None,
        assignee_id=task_in.assignee_id,
        deadline=norm_task_deadline_str or task_in.deadline,
        estimated_hours=task_in.estimated_hours,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
