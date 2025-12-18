from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.orchestration_access_matrix import OrchestrationAccessMatrix
from app.schemas.orchestration_access_matrix import AccessMatrixCreate, AccessMatrixUpdate

def get_all_access(db: Session):
    return db.query(OrchestrationAccessMatrix).all()

def get_access_by_id(db: Session, id: int):
    access = db.query(OrchestrationAccessMatrix).filter(OrchestrationAccessMatrix.id == id).first()
    if not access:
        raise HTTPException(status_code=404, detail="Access record not found")
    return access

#def create_access(db: Session, access: AccessMatrixCreate):
    #db_access = OrchestrationAccessMatrix(**access.dict())
   # db.add(db_access)
    #db.commit()
   # db.refresh(db_access)
   # return db_access

def create_access(db: Session, matrix: AccessMatrixCreate):
    db_matrix = OrchestrationAccessMatrix(
        role_name=matrix.role_name,
        sub_functionality_name=matrix.sub_functionality_name,
        action_type=matrix.action_type,
        action_flag=matrix.action_flag
    )
    db.add(db_matrix)
    db.commit()
    db.refresh(db_matrix)  # get auto-incremented id
    return db_matrix
def update_access(db: Session, id: int, access_update: AccessMatrixUpdate):
    access = db.query(OrchestrationAccessMatrix).filter(OrchestrationAccessMatrix.id == id).first()
    if not access:
        raise HTTPException(status_code=404, detail="Access record not found")

    for key, value in access_update.dict(exclude_unset=True).items():
        setattr(access, key, value)

    db.commit()
    db.refresh(access)
    return access

def delete_access(db: Session, id: int):
    access = db.query(OrchestrationAccessMatrix).filter(OrchestrationAccessMatrix.id == id).first()
    if not access:
        raise HTTPException(status_code=404, detail="Access record not found")

    db.delete(access)
    db.commit()
    return {"message": "Access record deleted successfully"}