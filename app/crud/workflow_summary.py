
# app/crud/workflow_summary.py
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, asc
from app.models.genrocket_services_details import GenRocketServicesDetails

def get_workflow_summary_by_project(
    db: Session,
    project_name: str,
    project_id: Optional[int] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    case_insensitive: bool = False,
) -> Tuple[str, int, List[Tuple[int, str]]]:
    """
    (Existing) Returns (project_name, project_id, workflows=[(workflow_id, workflow_name), ...]) for the project.
    Kept intact for backward compatibility.
    """
    # ... your existing implementation stays AS-IS ...
    # (no changes here)
    pass  # <-- remove this; your function body stays intact


# -------------------------------------------------
# ✅ NEW: Workflows list by a given project_id
# -------------------------------------------------
def get_workflow_summary_by_project_id(
    db: Session,
    project_id: int,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Tuple[str, int, List[Tuple[int, str]]]:
    """
    Returns (project_name, project_id, workflows=[(workflow_id, workflow_name), ...]) for the given project_id.
    Filters out rows where workflow_id or workflow_name are NULL.
    """
    if project_id is None or project_id <= 0:
        raise ValueError("project_id must be a positive integer")

    stmt = (
        select(
            GenRocketServicesDetails.project_name,
            GenRocketServicesDetails.project_id,
            GenRocketServicesDetails.workflow_id,
            GenRocketServicesDetails.workflow_name,
        )
        .where(GenRocketServicesDetails.project_id == project_id)
        .where(GenRocketServicesDetails.workflow_id.isnot(None))
        .where(GenRocketServicesDetails.workflow_name.isnot(None))
        .order_by(asc(GenRocketServicesDetails.workflow_name))
    )

    if offset is not None:
        stmt = stmt.offset(offset)
    if limit is not None:
        stmt = stmt.limit(limit)

    rows = db.execute(stmt).all()
    if not rows:
        # Caller (router) will translate to 404
        return ("", -1, [])

    # Choose a stable project_name (if multiple variants exist, pick min lexicographically)
    names = {r[0] for r in rows if r[0] is not None}
    project_name = min(names) if names else ""

    workflows: List[Tuple[int, str]] = []
    for (_, _, wid, wname) in rows:
        if wid is not None and wname is not None:
            workflows.append((wid, wname))

    return (project_name, project_id, workflows)
