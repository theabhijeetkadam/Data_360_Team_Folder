
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
        path = request.url.path
        method = request.method.upper()
        logger.info(f"[RBAC-GOV] start path={path}, method={method}")

        # ✅ Skip documentation routes
        if request.url.path in ["/", "/docs", "/openapi.json", "/redoc","/auth/login"]:
            logger.info("Skipping RBAC for documentation routes")
            return await call_next(request)

        # ✅ Skip any login path regardless of base segments (substring match)
        # Covers: /auth/login, /auth/auth/login, /Project_Management_Module/3/auth/login, etc.
        if "auth/login" in path:
            logger.info(f"[RBAC-GOV] whitelisted (auth login): {path}")
            return await call_next(request)

        # ✅ Skip orchestration routes (governance RBAC should not handle these)
        orchestration_prefixes = [
            "/api/execute-genrocket-service",
            "/tdm-tools",
            "/tdm_tool_services_field",
            "/genrocket_services_details",
            "/genrocket_services_execution_details",
            "/orchestration-delete-logs",
        ]
        if any(path.startswith(prefix) for prefix in orchestration_prefixes):
            logger.info(f"[RBAC-GOV] skipped (orchestration route): {path}")
            return await call_next(request)

        # ✅ Extract route segment; support an optional /api prefix
        segments = path.strip("/").split("/")
        if not segments:
            logger.info("[RBAC-GOV] no segments; skipping")
            return await call_next(request)
        route_segment = segments[1] if len(segments) > 1 and segments[0].lower() == "api" else segments[0]
        logger.info(f"[RBAC-GOV] route_segment={route_segment}")

        # ✅ Resolve governance feature mapping
        feature_name = FEATURE_MAP.get(route_segment)
        if not feature_name:
            logger.info(f"[RBAC-GOV] no governance feature mapping for route={route_segment}; skipping RBAC/header")
            # ⬅️ IMPORTANT: Do not enforce X-User-Id for unmapped routes
            return await call_next(request)

        # ✅ Map HTTP method to action
        action_map = {
            "POST": "CREATE",
            "PUT": "UPDATE",
            "PATCH": "UPDATE",
            "GET": "VIEW",
            "DELETE": "DELETE",
        }
        action_type = action_map.get(method, "VIEW")
        logger.info(f"[RBAC-GOV] action_type={action_type} feature_name={feature_name}")

        # ✅ Validate user header ONLY for governance-mapped routes
        user_id = request.headers.get("X-User-Id")
        if not user_id:
            logger.error("[RBAC-GOV] Missing X-User-Id header")
            return JSONResponse(status_code=401, content={"code": "401", "message": "Missing X-User-Id header"})

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
                logger.error(f"[RBAC-GOV] user not found: user_id={user_id}")
                return JSONResponse(status_code=404, content={"code": "404", "message": "User not found"})

            role_name = role_row[0]
            logger.info(f"[RBAC-GOV] user_id={user_id} role={role_name}")

            # ✅ Check permission in Feature_Role_Access_Matrix
            perm_row = self.db_session.execute(
                text("""
                    SELECT action_flag
                    FROM public.Feature_Role_Access_Matrix
                    WHERE role = :role AND feature_name = :feature AND action_type = :action
                """),
                {"role": role_name, "feature": feature_name, "action": action_type}
            ).fetchone()

            logger.info(f"[RBAC-GOV] action flag={perm_row}")


            # ✅ Access denied
            if not perm_row or not perm_row[0]:
                logger.warning(
                    f"[RBAC-GOV] access denied: user_id={user_id}, role={role_name}, feature={feature_name}, action={action_type}"
                )
                return JSONResponse(status_code=403, content={"code": "403", "message": "Access denied"})

            logger.info(
                f"[RBAC-GOV] access granted: user_id={user_id}, role={role_name}, feature={feature_name}, action={action_type}"
                )

        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"[RBAC-GOV] RBAC check failed: {str(e)}")
            return JSONResponse(status_code=500, content={"code": "500", "message": "RBAC check failed"})

# ✅ IMPORTANT: if we reach here, RBAC passed → continue to actual route
        response = await call_next(request)
        return response