from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app.database import get_db
from app.schemas import project_mi_view_DB

router = APIRouter(
    prefix="/db_project_summary",
    tags=["DB Project Summary"]
)

@router.get("/", response_model=List[project_mi_view_DB.ProjectSummaryDB])
def get_project_summary(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            project_name, 
             COUNT(DISTINCT workflow_name) AS number_of_workflows,
             COUNT(DISTINCT module_name) AS number_of_modules
        FROM db_orchestration_workflows 
        GROUP BY project_name
    """)
    result = db.execute(query).fetchall()
    
    return [
        {
            "project_name": row.project_name,
             "number_of_workflows": row.number_of_workflows,
            "number_of_modules": row.number_of_modules
           
        }
        for row in result
    ]
