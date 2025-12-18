from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.project import Project
from app.schemas.project import ProjectCreate

def create_project(db: Session, project: ProjectCreate):
    # Check for duplicate project_name
    existing_project_name = db.query(Project).filter(Project.project_name == project.project_name).first()
    if existing_project_name:
        raise HTTPException(status_code=400, detail="Project with same name already in use. Choose a different one.")

    # Check for duplicate module_name within the same project
    existing_module_name = db.query(Project).filter(Project.project_name == project.project_name,
                                                    Project.module_name == project.module_name).first()
    if existing_module_name:
        raise HTTPException(status_code=400, detail="Module with same name already exists in this project.")

    # Enforce module limit (max 4 per project)
    module_count = db.query(Project).filter(Project.project_name == project.project_name).count()
    if module_count >= 4:
        raise HTTPException(status_code=400, detail="Cannot add more than 4 modules to a single project.")

    # Generate module_id and scenario_id
    last_module = db.query(Project).order_by(Project.module_id.desc()).first()
    module_id = (last_module.module_id + 1) if last_module else 1

    last_scenario = db.query(Project).order_by(Project.scenario_id.desc()).first()
    scenario_id = (last_scenario.scenario_id + 1) if last_scenario else 1

    db_project = Project(
        **project.dict(),
        module_id=module_id,
        scenario_id=scenario_id
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_project(db: Session, project_id: int):
    return db.query(Project).filter(Project.project_id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Project).offset(skip).limit(limit).all()

def update_project(db: Session, project_id: int, project: ProjectCreate):
    db_project = db.query(Project).filter(Project.project_id == project_id).first()
    if db_project:
        for key, value in project.dict().items():
            setattr(db_project, key, value)
        db.commit()
        db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = db.query(Project).filter(Project.project_id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}
