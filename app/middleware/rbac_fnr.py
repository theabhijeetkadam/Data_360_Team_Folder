
# app/middleware/rbac_fnr.py

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config_fnr import FEATURE_MAP_FNR

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def _normalize_path(path: str) -> str:
    # ensure leading slash, no trailing slash
    clean = "/" + path.strip().strip("/")
    return clean

class FNRRBACMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db_session: Session):
        super().__init__(app)
        self.db_session = db_session
        # ✅ Public endpoints: skip header & RBAC checks
        self.public_paths = {
            "/", "/docs", "/openapi.json", "/redoc",
            "/auth/login",  # allow login without X-User-Id
        }

    async def dispatch(self, request: Request, call_next):
        path = _normalize_path(request.url.path)
        method = request.method.upper()
        logger.info(f"[RBAC-FNR] start path={path}, method={method}")

        # ✅ Skip documentation & public endpoints
        if request.url.path in ["/", "/docs", "/openapi.json", "/redoc","/auth/login","/project_summary"]:
            logger.info("Skipping RBAC for documentation routes")
            return await call_next(request)

        # ✅ Extract first segment (handle /api/<segment> prefixed routes)
        segments = path.strip("/").split("/")
        if not segments:
            return await call_next(request)

        route_segment = segments[1] if len(segments) > 1 and segments[0].lower() == "api" else segments[0]
        route_segment = route_segment.lower()
        logger.info(f"[RBAC-FNR] route_segment={route_segment}")

        # ✅ Check if this route participates in FnR RBAC
        feature_name = FEATURE_MAP_FNR.get(route_segment)
        if not feature_name:
            logger.info(f"[RBAC-FNR] no FnR RBAC mapping for segment: {route_segment}. Skipping RBAC.")
            # Do NOT enforce X-User-Id for non-FnR routes
            return await call_next(request)

        # ✅ Validate user header ONLY for FnR-mapped routes
        user_id = request.headers.get("X-User-Id")
        if not user_id:
            logger.error("[RBAC-FNR] Missing X-User-Id header")
            return JSONResponse(status_code=401, content={"code": "401", "message": "Missing X-User-Id header"})

        # ✅ Determine action type per mining_access_matrix
        lowered_path = path.lower()
        execute_keywords = ("execute", "run", "start", "trigger")
        if any(kw in lowered_path for kw in execute_keywords):
            action_type = "Execute"
        else:
            action_map = {
                "POST": "Create",
                "PUT": "Update",
                "PATCH": "Update",
                "GET": "View",   # mining_access_matrix uses "View"
                "DELETE": "Delete",
            }
            action_type = action_map.get(method, "View")

        logger.info(f"[RBAC-FNR] feature_name={feature_name}, action_type={action_type}")

        try:
            # ✅ Fetch user role (same approach as governance/orchestration)
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
                logger.error(f"[RBAC-FNR] user not found: user_id={user_id}")
                return JSONResponse(status_code=404, content={"code": "404", "message": "User not found"})

            role_name = role_row[0]
            logger.info(f"[RBAC-FNR] user_id={user_id} role={role_name}")

            # ✅ Check permission in mining_access_matrix (boolean flag)
            perm_row = self.db_session.execute(
                text("""
                    SELECT action_flag
                    FROM clientdb.mining_access_matrix
                    WHERE role_name = :role
                      AND sub_functionality_name = :feature
                      AND action_type = :action
                    LIMIT 1
                """),
                {"role": role_name, "feature": feature_name, "action": action_type}
            ).fetchone()

            if not perm_row:
                logger.warning(
                    f"[RBAC-FNR] matrix row not found: role={role_name}, feature={feature_name}, action={action_type}"
                )
                return JSONResponse(status_code=403, content={"code": "403", "message": "Access denied"})

            # action_flag is BOOLEAN → allow True only
            flag = perm_row[0]
            if not bool(flag):
                logger.warning(
                    f"[RBAC-FNR] access denied: user_id={user_id}, role={role_name}, feature={feature_name}, action={action_type}"
                )
                return JSONResponse(status_code=403, content={"code": "403", "message": "Access denied"})

            logger.info(
                f"[RBAC-FNR] access granted: user_id={user_id}, role={role_name}, feature={feature_name}, action={action_type}"
            )

        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"[RBAC-FNR] RBAC check failed: {str(e)}")
            return JSONResponse(status_code=500, content={"code": "500", "message": "RBAC check failed"})

        # ✅ IMPORTANT: if we reach here, RBAC passed → continue to actual route
        response = await call_next(request)
        return response
