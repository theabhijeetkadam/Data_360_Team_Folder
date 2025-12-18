
# app/crud/distinct_value.py

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.distinct_value import MiningWorkflowInputCriteria
import re

# ---------- ORM helper: criteria lookups in clientdb ----------
def get_criteria_by_business_name(db: Session, workflow_id: int, business_name: str):
    """
    Returns criteria rows matching workflow_id and business_name (from clientdb.mining_workflow_input_criteria_1),
    or all for the workflow if 'Any' is passed.
    """
    q = db.query(MiningWorkflowInputCriteria).filter(MiningWorkflowInputCriteria.workflow_id == workflow_id)
    if business_name.lower() != "any":
        q = q.filter(MiningWorkflowInputCriteria.business_name == business_name)
    return q.all()

# ---------- Raw SQL helper: distinct values from source schema ----------
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

def _safe_ident(name: str) -> str:
    if not name or not IDENT_RE.match(name):
        raise ValueError(f"Invalid identifier: {name!r}")
    return f'"{name}"'

def get_value_from_source_table(db: Session, source_schema: str, source_table: str, source_column: str):
    """
    Fetch distinct values from the given source schema.table.column.
    Defaults to gold_copy at call sites if schema not provided.
    """
    schema_ident = _safe_ident(source_schema.strip().lower())
    table_ident  = _safe_ident(source_table.strip().lower())
    column_ident = _safe_ident(source_column.strip().lower())

    sql = text(f"""
        SELECT DISTINCT {column_ident}
        FROM {schema_ident}.{table_ident}
        WHERE {column_ident} IS NOT NULL
        ORDER BY {column_ident} ASC
       """)
    result = db.execute(sql).fetchall()
