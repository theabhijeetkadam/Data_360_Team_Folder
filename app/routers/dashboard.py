
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.project import Project

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/{project_id}")
def project_dashboard(project_id: int, db: Session = Depends(get_db)):
    # Fetch project details
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Fetch up to 4 modules for the project from the same table
    modules = db.query(Project).filter(Project.project_name == project.project_name).limit(4).all()

    return {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "modules": [
            {
                "module_id": m.module_id,
                "module_name": m.module_name
            }
            for m in modules
        ]
    }