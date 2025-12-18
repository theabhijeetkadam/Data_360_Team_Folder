from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.mining_fields_type import MiningFieldsType
from app.schemas.mining_fields_type import MiningFieldsTypeCreate, MiningFieldsTypeUpdate

#def create_field_type(db: Session, request: MiningFieldsTypeCreate):
    #existing = db.query(MiningFieldsType).filter(MiningFieldsType.type_of_field == request.type_of_field).first()
    #f existing:
       # raise HTTPException(status_code=400, detail="Field type already exists")

    #new_field = MiningFieldsType(type_of_field=request.type_of_field)
    #db.add(new_field)
    #db.commit()
    #db.refresh(new_field)
    #return new_field

def get_all_field_types(db: Session):
    return db.query(MiningFieldsType).all()

#def get_field_type_by_id(db: Session, field_id: int):
   ###return record

#def update_field_type(db: Session, field_id: int, request: MiningFieldsTypeUpdate):
   # record = db.query(MiningFieldsType).filter(MiningFieldsType.field_id == field_id).first()
    #if not record:
        #raise HTTPException(status_code=404, detail="Field type not found")

    # Prevent duplicates
    #######record.type_of_field = request.type_of_field
    #db.commit()
    #db.refresh(record)
    #return record

#def delete_field_type(db: Session, field_id: int):
    #record = db.query(MiningFieldsType).filter(MiningFieldsType.field_id == field_id).first()
    #if not record:
       # raise HTTPException(status_code=404, detail="Field type not found")

   # db.delete(record)
    #db.commit()
    #return {"detail": "Field type deleted successfully"}
