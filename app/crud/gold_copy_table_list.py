
# app/crud/source_schema.py
from sqlalchemy.orm import Session
from sqlalchemy import text

def list_tables_in_schema(db: Session, schema: str = "gold_copy") -> list[str]:
    """
    Returns all base table names from the given PostgreSQL schema.
    Defaults to 'gold_copy'.
    """
    sql = text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = :schema
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    rows = db.execute(sql, {"schema": schema}).fetchall()
    return [r[0] for r in rows]


def get_columns_by_table(db: Session, table: str, schema: str = "gold_copy") -> list[str]:
    """
    Returns column names for the given schema.table ordered by ordinal position.
    """
    sql = text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = :schema
          AND table_name   = :table
        ORDER BY ordinal_position;
    """)
    rows = db.execute(sql, {"schema": schema, "table": table}).fetchall()
    return [r[0] for r in rows]


# (Optional) If you want types along with names
def get_columns_with_types(db: Session, table: str, schema: str = "gold_copy") -> list[dict]:
    """
    Returns columns with data types and nullable flag.
    """
    sql = text("""
        SELECT
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = :schema
          AND table_name   = :table
        ORDER BY ordinal_position;
    """)
    rows = db.execute(sql, {"schema": schema, "table": table}).mappings().all()
    return [dict(r) for r in rows]
