from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
#from app.database import get_db
from app.database import SessionLocal
from app.schemas import mining_fields_type as schema
from app.crud import mining_fields_type as crud

router = APIRouter(prefix="/field-types", tags=["Mining Fields Type"])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def error_response(code: int, message: str):
    return {"code": str(code), "message": message}

#@router.post("/", response_model=schema.MiningFieldsTypeResponse)
#def create_field_type(request: schema.MiningFieldsTypeCreate, db: Session = Depends(get_db)):
    #return crud.create_field_type(db, request)

@router.get("/", response_model=list[schema.MiningFieldsTypeResponse])
def get_all_field_types(db: Session = Depends(get_db)):
    return crud.get_all_field_types(db)

#@router.get("/{field_id}", response_model=schema.MiningFieldsTypeResponse)
#def get_field_type_by_id(field_id: int, db: Session = Depends(get_db)):
    #return crud.get_field_type_by_id(db, field_id)

#@router.put("/{field_id}", response_model=schema.MiningFieldsTypeResponse)
#def update_field_type(field_id: int, request: schema.MiningFieldsTypeUpdate, db: Session = Depends(get_db)):
    #return crud.update_field_type(db, field_id, request)

#@router.delete("/{field_id}")
#def delete_field_type(field_id: int, db: Session = Depends(get_db)):
    #return crud.delete_field_type(db, field_id)
