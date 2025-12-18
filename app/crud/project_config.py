from sqlalchemy.orm import Session
from app.models.project_config import ProjectConfig
from app.schemas.project_config import ProjectConfigCreate
from fastapi import HTTPException

def create_project_config(db: Session, config: ProjectConfigCreate):
    db_config = ProjectConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def get_project_config(db: Session, config_id: int):
    return db.query(ProjectConfig).filter(ProjectConfig.config_id == config_id).first()

def get_project_configs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ProjectConfig).offset(skip).limit(limit).all()

def update_project_config(db: Session, config_id: int, config: ProjectConfigCreate):
    db_config = db.query(ProjectConfig).filter(ProjectConfig.config_id == config_id).first()
    if db_config:
        for key, value in config.dict().items():
            setattr(db_config, key, value)
        db.commit()
        db.refresh(db_config)
    return db_config

def delete_project_config(db: Session, config_id: int):
    db_config = db.query(ProjectConfig).filter(ProjectConfig.config_id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="project not found")
    db.delete(db_config)
    db.commit()
    return {"message": "Project deleted successfully"}
