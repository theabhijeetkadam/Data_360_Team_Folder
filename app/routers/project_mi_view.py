
# app/routers/project_mi_view.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app.database import get_db
from app.schemas import project_mi_view

router = APIRouter(
    prefix="/project_summary",
    tags=["Orchestration Project Summary"]
)

@router.get("/", response_model=List[project_mi_view.ProjectSummary])
def get_project_summary(db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT
                p.project_id,
                p.project_name,
                COUNT(DISTINCT g.module_name)  AS number_of_modules,
                COUNT(DISTINCT g.scenario)     AS number_of_scenarios
            FROM public.project_table AS p
            JOIN genrocket_services_details AS g
              ON g.project_id = p.project_id
            GROUP BY p.project_id, p.project_name
            ORDER BY p.project_id ASC;
        """)
        result = db.execute(query).mappings().all()
        return [
            {
                "project_id": row["project_id"],
                "project_name": row["project_name"],
                "number_of_modules": row["number_of_modules"],
                "number_of_scenarios": row["number_of_scenarios"],
            }
            for row in result
        ]
    except Exception as e:
        print("❌ Error in get_project_summary:", str(e))
