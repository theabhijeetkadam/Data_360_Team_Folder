
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.genrocket_services_details import GenRocketServicesDetails
from app.schemas.genrocket_services_details import GenRocketServicesDetailsCreate, GenRocketServicesDetailsUpdate
from app.exceptions import NotFoundError, DuplicateEntryError, DBInsertError, DBUpdateError, DBDeleteError, DBReadError

def get_all_services(db: Session):
    try:
        return db.query(GenRocketServicesDetails).all()
    except SQLAlchemyError as e:
        raise DBReadError(message=f"DB operation failed while reading services: {str(e)}")

def get_service_by_id(db: Session, workflow_id: int):
    try:
        service = db.query(GenRocketServicesDetails).filter(GenRocketServicesDetails.workflow_id == workflow_id).first()
        if not service:
            raise NotFoundError(message="Service not found", code="404")
        return service
    except SQLAlchemyError as e:
        raise DBReadError(message=f"DB operation failed while reading service: {str(e)}")

def create_service(db: Session, service: GenRocketServicesDetailsCreate):
    try:
        # Auto-generate IDs
        last_project = db.query(GenRocketServicesDetails).order_by(GenRocketServicesDetails.project_id.desc()).first()
        project_id = (last_project.project_id + 1) if last_project else 1

        last_module = db.query(GenRocketServicesDetails).order_by(GenRocketServicesDetails.module_id.desc()).first()
        module_id = (last_module.module_id + 1) if last_module else 1

        last_scenario = db.query(GenRocketServicesDetails).order_by(GenRocketServicesDetails.scenario_id.desc()).first()
        scenario_id = (last_scenario.scenario_id + 1) if last_scenario else 1
        db_service = GenRocketServicesDetails(
            **service.dict(),  # ✅ Includes workflow_name now
            project_id=project_id,
            module_id=module_id,
            scenario_id=scenario_id
        )
        db.add(db_service)
        db.commit()
        db.refresh(db_service)
        return db_service
    except IntegrityError:
        db.rollback()
        raise DuplicateEntryError(message="Duplicate entry detected", code="409")
    except SQLAlchemyError as e:
        db.rollback()
        raise DBInsertError(message=f"DB operation failed while creating service: {str(e)}", code="500")
def update_service(db: Session, workflow_id: int, service: GenRocketServicesDetailsUpdate):
    try:
        db_service = db.query(GenRocketServicesDetails).filter(GenRocketServicesDetails.workflow_id == workflow_id).first()
        if not db_service:
            raise NotFoundError(message="Service not found", code="404")

        for key, value in service.model_dump(exclude_unset=True).items():
            setattr(db_service, key, value)

        db.commit()
        db.refresh(db_service)
        return db_service
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise DBUpdateError(message=f"DB operation failed while updating service: {str(e)}", code="500")

def delete_service(db: Session, workflow_id: int):
    try:
        db_service = db.query(GenRocketServicesDetails).filter(GenRocketServicesDetails.workflow_id == workflow_id).first()
        if not db_service:
            raise NotFoundError(message="Service not found", code="404")

        db.delete(db_service)
        db.commit()
        return db_service
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise DBDeleteError(message=f"DB operation failed while deleting service: {str(e)}", code="500")
