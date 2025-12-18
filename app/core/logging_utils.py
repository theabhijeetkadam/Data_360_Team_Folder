from datetime import datetime
from app.models import deletelog
from sqlalchemy.orm import Session
from app.exceptions import (
    DuplicateEntryError, DBInsertError, DBReadError,
    DBUpdateError, DBDeleteError
)
def log_deletion(db: Session, module_name: str, record_id: int, deleted_by_userid: int, deleted_by_username: str):
   try: 
      log = deletelog(
        deleted_by_userid=deleted_by_userid,
        deleted_by_username=deleted_by_username,
        deleted_date=datetime.utcnow().date(),
        deleted_time=datetime.utcnow().time(),
        module_name=module_name,
        record_id=record_id
      )
      db.add(log)
      db.commit()
   except Exception as e:
        db.rollback()
        raise DBInsertError(message=f"Unexpected DB error: {str(e)}")
