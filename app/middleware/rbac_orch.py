import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config_orch import FEATURE_MAP_ORCHESTRATION

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class OrchestrationRBACMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db_session: Session):
        super().__init__(app)
        self.db_session = db_session

    async def dispatch(self, request: Request, call_next):
        logger.info(f"Orchestration RBAC check started for path: {request.url.path}, method: {request.method}")

        # ✅ Skip documentation routes
        if request.url.path in ["/", "/docs", "/openapi.json", "/redoc", "/auth/login"]:
            return await call_next(request)

        # ✅ Validate user header
        user_id = request.headers.get("X-User-Id")
        if not user_id:
            logger.error("Missing X-User-Id header")
            return JSONResponse(status_code=401, content={"code": "401", "message": "Missing X-User-Id header"})

        # ✅ Extract route segment and handle prefix like /api
        segments = request.url.path.strip("/").split("/")
        route_segment = segments[1] if len(segments) > 1 and segments[0] == "api" else segments[0]

        # ✅ Check if route is mapped for orchestration RBAC
        feature_name = FEATURE_MAP_ORCHESTRATION.get(route_segment)
        if not feature_name:
            logger.info(f"No orchestration RBAC mapping for route: {route_segment}. Skipping orchestration RBAC.")
            return await call_next(request)  # ✅ Do NOT proceed with DB checks

        # ✅ Determine action type
        if "execute" in request.url.path or "run" in request.url.path:
            action_type = "Execute"
        else:
            action_map = {
                "POST": "Create",
                "PUT": "Update",
                "PATCH": "Update",
                "GET": "Read",
                "DELETE": "Delete"
            }
            action_type = action_map.get(request.method.upper(), "Read")

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
                    FROM orchestration_access_matrix
                    WHERE role_name = :role AND sub_functionality_name = :feature AND action_type = :action
                """),
                {"role": role_name, "feature": feature_name, "action": action_type}
            ).fetchone()

            if not perm_row or perm_row[0].lower() != "yes":
                logger.warning(f"Access denied: user_id={user_id}, role={role_name}, feature={feature_name}, action={action_type}")
                return JSONResponse(status_code=403, content={"code": "403", "message": "Access denied"})

            logger.info(f"Access granted: user_id={user_id}, feature={feature_name}, action={action_type}")

        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"RBAC check failed: {str(e)}")
            return JSONResponse(status_code=500, content={"code": "500", "message": "RBAC check failed"})

        return await call_next(request)