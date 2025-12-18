from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.project import ProjectCreate
from app.crud.project import (
    create_project, get_project, get_projects,
    update_project, delete_project
)
from app.exceptions import NotFoundError

router = APIRouter(prefix="/Project_Management_Module", tags=["Projects"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Helper to convert SQLAlchemy object to dict
def to_dict(obj):
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

# ✅ Create Project
@router.post("/", response_model=dict)
def create(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = create_project(db, project)
    return {
        "message": "Project created successfully.",
        "data": to_dict(db_project)
    }

# ✅ Read Project by ID
@router.get("/{project_id}", response_model=dict)
def read(project_id: int, db: Session = Depends(get_db)):
    db_project = get_project(db, project_id)
    if not db_project:
        raise NotFoundError(message="Project not found", code="ERR_004")
    return {
        "message": "Project details retrieved successfully.",
        "data": to_dict(db_project)
    }

# ✅ Read All Projects
@router.get("/", response_model=dict)
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = get_projects(db, skip, limit)
    return {
        "message": "Project list retrieved successfully.",
        "data": [to_dict(p) for p in projects]
    }

# ✅ Update Project
@router.put("/{project_id}", response_model=dict)
def update(project_id: int, project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = update_project(db, project_id, project)
    if not db_project:
        raise NotFoundError(message="Resource to update not found", code="ERR_007")
    return {
        "message": "Project updated successfully.",
        "data": to_dict(db_project)
    }

# ✅ Delete Project
@router.delete("/{project_id}", response_model=dict)
def delete(project_id: int, db: Session = Depends(get_db)):
    db_project = delete_project(db, project_id)
    if not db_project:
        raise NotFoundError(message="Resource to delete not found", code="ERR_009")
    return {
        "message": "Project deleted successfully.",
        "data": to_dict(db_project)
    }