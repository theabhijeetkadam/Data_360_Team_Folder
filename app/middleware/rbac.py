import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import FEATURE_MAP

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class RBACMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db_session: Session):
        super().__init__(app)
        self.db_session = db_session

    async def dispatch(self, request: Request, call_next):
        logger.info(f"RBAC check started for path: {request.url.path}, method: {request.method}")

        # ✅ Skip documentation routes
        if request.url.path in ["/", "/docs", "/openapi.json", "/redoc","/auth/login"]:
            logger.info("Skipping RBAC for documentation routes")
            return await call_next(request)

        # ✅ Skip orchestration routes
        orchestration_prefixes = [
            "/api/execute-genrocket-service",
            "/tdm-tools",
            "/tdm_tool_services_field",
            "/genrocket_services_details",
            "/genrocket_services_execution_details",
            "/orchestration-delete-logs"
        ]
        if any(request.url.path.startswith(prefix) for prefix in orchestration_prefixes):
            logger.info(f"Skipping Governance RBAC for orchestration route: {request.url.path}")
            return await call_next(request)

        # ✅ Validate user header
        user_id = request.headers.get("X-User-Id")
        if not user_id:
            logger.error("Missing X-User-Id header")
            return JSONResponse(status_code=401, content={"code": "401", "message": "Missing X-User-Id header"})

        # ✅ Map HTTP method to action
        action_map = {
            "POST": "CREATE",
            "PUT": "UPDATE",
            "PATCH": "UPDATE",
            "GET": "VIEW",
            "DELETE": "DELETE"
        }
        action_type = action_map.get(request.method.upper(), "VIEW")
        logger.info(f"Action type resolved: {action_type}")

        # ✅ Extract route segment
        segments = request.url.path.strip("/").split("/")
        route_segment = segments[0] if segments else None

        feature_name = FEATURE_MAP.get(route_segment)
        if not feature_name:
            logger.info(f"No RBAC feature mapping for route: {route_segment}")
            return await call_next(request)

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

            # ✅ User not found
            if not role_row:
                logger.error(f"User not found: user_id={user_id}")
                return JSONResponse(status_code=404, content={"code": "404", "message": "User not found"})

            role_name = role_row[0]
            logger.info(f"User {user_id} has role: {role_name}")

            # ✅ Check permission in Feature_Role_Access_Matrix
            perm_row = self.db_session.execute(
                text("""
                    SELECT action_flag
                    FROM Feature_Role_Access_Matrix
                    WHERE role = :role AND feature_name = :feature AND action_type = :action
                """),
                {"role": role_name, "feature": feature_name, "action": action_type}
            ).fetchone()

            # ✅ Access denied
            if not perm_row or not perm_row[0]:
                logger.warning(f"Access denied: user_id={user_id}, role={role_name}, feature={feature_name}, action={action_type}")
                return JSONResponse(status_code=403, content={"code": "403", "message": "Access denied"})

            logger.info(f"Access granted: user_id={user_id}, feature={feature_name}, action={action_type}")

        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"RBAC check failed: {str(e)}")
            return JSONResponse(status_code=500, content={"code": "500", "message": "RBAC check failed"})

        return await call_next(request)