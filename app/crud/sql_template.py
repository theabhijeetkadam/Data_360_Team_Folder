from sqlalchemy.orm import Session
from app.models.sql_template import SQLTemplate
from app.schemas import sql_template as schemas

def create_sql_template(db: Session, sql: schemas.SQLTemplateCreate):
    db_sql = SQLTemplate(**sql.dict())
    db.add(db_sql)
    db.commit()
    db.refresh(db_sql)
    return db_sql

def get_all_sql_templates(db: Session):
    return db.query(SQLTemplate).all()

def get_sql_template_by_id(db: Session, sql_id: int):
    return db.query(SQLTemplate).filter(SQLTemplate.sql_id == sql_id).first()

def update_sql_template(db: Session, sql_id: int, sql: schemas.SQLTemplateUpdate):
    db_sql = db.query(SQLTemplate).filter(SQLTemplate.sql_id == sql_id).first()
    if not db_sql:
        return None
    for field, value in sql.dict(exclude_unset=True).items():
        setattr(db_sql, field, value)
    db.commit()
    db.refresh(db_sql)
    return db_sql

def delete_sql_template(db: Session, sql_id: int):
    db_sql = db.query(SQLTemplate).filter(SQLTemplate.sql_id == sql_id).first()
    if not db_sql:
        return None
    db.delete(db_sql)
    db.commit()
    return db_sql
