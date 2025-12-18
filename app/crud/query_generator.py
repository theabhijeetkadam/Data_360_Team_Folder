
# app/crud/query_generator.py
from sqlalchemy.orm import Session
from app import models
from app.models.lock_unlock import ExtractedData as ExtractedDataTable

# -------------------------
# ExtractedDataTable CRUD
# -------------------------

def get_extracted_data(db: Session, data_key: int):
    """
    Fetch a single row by the internal primary key (data_key) from clientdb.extracted_data_table.
    """
    return (
        db.query(ExtractedDataTable)
          .filter(ExtractedDataTable.data_key == data_key)
          .first()
    )

def get_all_extracted_data(db: Session, skip: int = 0, limit: int = 100):
    """
    Fetch a paginated list of rows from clientdb.extracted_data_table.
    """
    return (
        db.query(ExtractedDataTable)
          .offset(skip)
          .limit(limit)
          .all()
    )

def create_extracted_data(db: Session, data: dict):
    """
    Create a row in clientdb.extracted_data_table.
    NOTE: This function commits immediately, preserving your existing behavior.
          If you want atomic multi-row inserts, remove commit here and commit once in the caller.
    """
    db_item = ExtractedDataTable(**data)
    db.add(db_item)
    db.commit()          # keep existing behavior
    db.refresh(db_item)
    return db_item

def update_extracted_data(db: Session, data_key: int, updated_data: dict):
    """
    Update a row (by data_key) in clientdb.extracted_data_table and commit.
    """
    db_item = (
        db.query(ExtractedDataTable)
          .filter(ExtractedDataTable.data_key == data_key)
          .first()
    )
    if db_item:
        for key, value in updated_data.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_extracted_data(db: Session, data_key: int):
    """
    Delete a row (by data_key) from clientdb.extracted_data_table and commit.
    """
    db_item = (
        db.query(ExtractedDataTable)
          .filter(ExtractedDataTable.data_key == data_key)
          .first()
    )
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item
