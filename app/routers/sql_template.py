from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import sql_template as schemas
from app.crud import sql_template as crud

router = APIRouter(
    prefix="/sql_templates",
    tags=["SQL Templates"]
)

@router.post("/", response_model=schemas.SQLTemplateResponse)
def create_sql(sql: schemas.SQLTemplateCreate, db: Session = Depends(get_db)):
    return crud.create_sql_template(db, sql)

@router.get("/", response_model=list[schemas.SQLTemplateResponse])
def get_all_sql(db: Session = Depends(get_db)):
    return crud.get_all_sql_templates(db)

@router.get("/{sql_id}", response_model=schemas.SQLTemplateResponse)
def get_sql_by_id(sql_id: int, db: Session = Depends(get_db)):
    sql = crud.get_sql_template_by_id(db, sql_id)
    if not sql:
        raise HTTPException(status_code=404, detail="SQL Template not found")
    return sql

@router.put("/{sql_id}", response_model=schemas.SQLTemplateResponse)
def update_sql(sql_id: int, sql: schemas.SQLTemplateUpdate, db: Session = Depends(get_db)):
    updated = crud.update_sql_template(db, sql_id, sql)
    if not updated:
        raise HTTPException(status_code=404, detail="SQL Template not found")
    return updated

@router.delete("/{sql_id}")
def delete_sql(sql_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_sql_template(db, sql_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="SQL Template not found")
    return {"message": "SQL Template deleted successfully"}

