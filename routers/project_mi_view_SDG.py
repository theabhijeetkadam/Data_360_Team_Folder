# app/routers/project_mi_view.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app.database import get_db
from app.schemas import project_mi_view_SDG

router = APIRouter(
    prefix="/project_summary_SDG",
    tags=["SDG Project Summary"]
)

@router.get("/", response_model=List[project_mi_view_SDG.ProjectSummarySDG])
def get_project_summary(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            project_name, 
            COUNT(DISTINCT module_name) AS number_of_modules, 
            COUNT(DISTINCT scenario_name) AS number_of_scenarios
        FROM workflows
        GROUP BY project_name
    """)
    result = db.execute(query).fetchall()
    
    return [
        {
            "project_name": row.project_name,
            "number_of_modules": row.number_of_modules,
            "number_of_scenarios": row.number_of_scenarios
        }
        for row in result
    ]
