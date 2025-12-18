
# app/routers/source_schema.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud.gold_copy_table_list import list_tables_in_schema, get_columns_by_table, get_columns_with_types


router = APIRouter(prefix="/gold_copy_tableList", tags=["Gold Copy Table List"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/tables")
def get_tables(schema: str = Query(default="gold_copy", description="PostgreSQL schema name")):
    """
    Returns a dynamic list of tables from the specified schema (default: gold_copy).
    Example: GET /source-schema/tables
             GET /source-schema/tables?schema=gold_copy
    """
    db: Session = next(get_db())
    try:
        tables = list_tables_in_schema(db, schema=schema)
        return {"schema": schema, "tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tables for schema '{schema}': {str(e)}")
    finally:
        db.close()


@router.get("/columns")
def get_columns(table: str = Query(..., description="Table name in the schema (e.g., 'customer')"),
                schema: str = Query(default="gold_copy", description="PostgreSQL schema name"),
                include_types: bool = Query(default=False, description="Return column data types as well"),
                db: Session = Depends(get_db)):
    """
    Returns columns for a given table in the specified schema.
    Example:
      GET /source-schema/columns?table=customer
      GET /source-schema/columns?table=customer&include_types=true
    """
    # Basic validation: check table exists in the schema first
    tables = list_tables_in_schema(db, schema=schema)
    if table not in tables:
        raise HTTPException(status_code=404, detail=f"Table '{table}' not found in schema '{schema}'")

    try:
        if include_types:
            cols = get_columns_with_types(db, table=table, schema=schema)
            return {"schema": schema, "table": table, "columns": cols}
        else:
            cols = get_columns_by_table(db, table=table, schema=schema)
            return {"schema": schema, "table": table, "columns": cols}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list columns for {schema}.{table}: {str(e)}")

