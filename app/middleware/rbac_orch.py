
# middleware/rbac_orch.py
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config_orch import FEATURE_MAP_ORCHESTRATION

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def _normalize_path(path: str) -> str:
    # ensure leading slash, no trailing slash
    clean = "/" + path.strip().strip("/")
    return clean

class OrchestrationRBACMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db_session: Session):
        super().__init__(app)
        self.db_session = db_session
        # ✅ Public endpoints: skip header & RBAC checks
        self.public_paths = {
            "/", "/docs", "/openapi.json", "/redoc",
            "/auth/login",  # ← allow login without X-User-Id
        }

    async def dispatch(self, request: Request, call_next):
        path = _normalize_path(request.url.path)
        method = request.method.upper()
        logger.info(f"Orchestration RBAC check started for path: {path}, method: {method}")

        # ✅ Skip documentation & public endpoints
        if request.url.path in ["/", "/docs", "/openapi.json", "/redoc","/auth/login"]:
            logger.info("Skipping RBAC for documentation routes")
            return await call_next(request)

        # ✅ Extract first segment (handle /api/<segment> prefixed routes)
        segments = path.strip("/").split("/")
        if not segments:
            return await call_next(request)

        route_segment = segments[1] if len(segments) > 1 and segments[0].lower() == "api" else segments[0]

        # ✅ Check if this route participates in orchestration RBAC
        feature_name = FEATURE_MAP_ORCHESTRATION.get(route_segment)
        if not feature_name:
            logger.info(f"No orchestration RBAC mapping for route: {route_segment}. Skipping orchestration RBAC.")
            # ⬅️ Important: do NOT enforce X-User-Id for non-orchestration routes
            return await call_next(request)

        # ✅ Validate user header ONLY for orchestration-mapped routes
        user_id = request.headers.get("X-User-Id")
        if not user_id:
            logger.error("Missing X-User-Id header")
            return JSONResponse(status_code=401, content={"code": "401", "message": "Missing X-User-Id header"})

        # ✅ Determine action type
        if "execute" in path or "run" in path:
            action_type = "Execute"
        else:
            action_map = {
                "POST": "Create",
                "PUT": "Update",
                "PATCH": "Update",
                "GET": "Read",
                "DELETE": "Delete"
            }
            action_type = action_map.get(method, "Read")

        try:
            # ✅ Fetch user role
            role_row = self.db_session.execute(
                text("""
                    SELECT ur.role_name
                    FROM user_role ur
                    JOIN user_table u ON u.role_id = ur.role_id
                    WHERE u.user_id = :user_id
                """),
                {"user_id": user_id}
            ).fetchone()

            if not role_row:
                logger.error(f"Role not found for user_id: {user_id}")
                return JSONResponse(status_code=404, content={"code": "404", "message": "User not found"})

            role_name = role_row[0]

            # ✅ Check permission in orchestration_access_matrix
            perm_row = self.db_session.execute(
                text("""
                    SELECT action_flag
                    FROM public.orchestration_access_matrix
                    WHERE role_name = :role AND sub_functionality_name = :feature AND action_type = :action
                """),
                {"role": role_name, "feature": feature_name, "action": action_type}
            ).fetchone()

            if not perm_row or str(perm_row[0]).lower() != "yes":
                logger.warning(
                    f"Access denied: user_id={user_id}, role={role_name}, feature={feature_name}, action={action_type}"
                )
                return JSONResponse(status_code=403, content={"code": "403", "message": "Access denied"})

            logger.info(f"Access granted: user_id={user_id}, feature={feature_name}, action={action_type}")

        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"RBAC check failed: {str(e)}")
            return JSONResponse(status_code=500, content={"code": "500", "message": "RBAC check failed"})

# ✅ IMPORTANT: if we reach here, RBAC passed → continue to actual route

        response = await call_next(request)

        return response
 