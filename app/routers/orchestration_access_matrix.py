from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.orchestration_access_matrix import AccessMatrixCreate, AccessMatrixUpdate, AccessMatrixResponse
from app.crud import orchestration_access_matrix as crud
from fastapi import  HTTPException
from app import crud
from app.models.orchestration_access_matrix import OrchestrationAccessMatrix
from app import crud,schemas
from app.crud.orchestration_access_matrix import get_all_access
from app.crud.orchestration_access_matrix import (
    update_access, get_all_access, get_access_by_id,
    create_access,delete_access
)


router = APIRouter(prefix="/access_matrix", tags=["Orchestration Access Matrix"])

#@router.get("/", response_model=list[AccessMatrixResponse])
#def read_all(db: Session = Depends(get_db)):
   # return crud.get_all_access(db)

@router.get("/access_matrix/")
def read_access_matrix(db: Session = Depends(get_db)):
    return get_all_access(db)

#@router.get("/{id}", response_model=AccessMatrixResponse)
#def read(id: int, db: Session = Depends(get_db)):
   # return crud.get_access_by_id(db, id)

@router.get("/access_matrix/{id}")
def read(id: int, db: Session = Depends(get_db)):
    return get_access_by_id(db, id)

#@router.post("/", response_model=AccessMatrixResponse, status_code=201)
#def create_access(access: AccessMatrixCreate, db: Session = Depends(get_db)):
# return crud.create_access(db, access)

@router.post("/", response_model=AccessMatrixResponse)
def create(matrix: AccessMatrixCreate, db: Session = Depends(get_db)):
    return create_access(db=db, matrix=matrix)

@router.put("/{id}", response_model=AccessMatrixResponse)
def update(id: int, access: AccessMatrixUpdate, db: Session = Depends(get_db)):
    return update_access(db, id, access)

@router.delete("/{id}")
def delete(id: int, db: Session = Depends(get_db)):
    return delete_access(db, id)