from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.middleware.rbac import RBACMiddleware
from app.middleware.rbac_orch import OrchestrationRBACMiddleware
from app.database import SessionLocal  # SQLAlchemy session factory
from fastapi.exceptions import RequestValidationError
from app.exceptions import (
    ValidationError, DuplicateEntryError, DBInsertError, NotFoundError,
    DBReadError, DBUpdateError, DBDeleteError, UnknownError, AccessDeniedError
)
from app.routers import environment_instance
from app.routers import status
from .routers import dashboard
from .models import project
from app.routers import user, auth

# ✅ Create DB session for middleware
db_session = SessionLocal()

# ✅ Initialize FastAPI app
app = FastAPI(
    title="Data360 Governance & Orchestration API",
    description="Backend for Data360 Governance and Orchestration modules",
    version="1.0.0"
)

# ✅ Add RBAC Middlewares
app.add_middleware(RBACMiddleware, db_session=db_session)  # Governance RBAC
app.add_middleware(OrchestrationRBACMiddleware, db_session=db_session)  # Orchestration RBAC

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Error Response Helper
def create_error_response(status_code: int, code: str, message: str):
    return JSONResponse(
        status_code=status_code,
        content={"code": code, "message": message}
    )

# ✅ Exception Handlers
@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc: ValidationError):
    return create_error_response(400, exc.code, exc.message)

@app.exception_handler(DuplicateEntryError)
async def duplicate_error_handler(request, exc: DuplicateEntryError):
    return create_error_response(409, exc.code, exc.message)

@app.exception_handler(DBInsertError)
async def db_insert_error_handler(request, exc: DBInsertError):
    return create_error_response(500, exc.code, exc.message)

@app.exception_handler(NotFoundError)
async def not_found_error_handler(request, exc: NotFoundError):
    return create_error_response(404, exc.code, exc.message)

@app.exception_handler(DBReadError)
async def db_read_error_handler(request, exc: DBReadError):
    return create_error_response(500, exc.code, exc.message)

@app.exception_handler(DBUpdateError)
async def db_update_error_handler(request, exc: DBUpdateError):
    return create_error_response(500, exc.code, exc.message)

@app.exception_handler(DBDeleteError)
async def db_delete_error_handler(request, exc: DBDeleteError):
    return create_error_response(409, exc.code, exc.message)

@app.exception_handler(UnknownError)
async def unknown_error_handler(request, exc: UnknownError):
    return create_error_response(500, exc.code, exc.message)

@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"code": "400", "message": "Input data is invalid or missing", "details": exc.errors()}
    )

@app.exception_handler(AccessDeniedError)
async def access_denied_error_handler(request, exc: AccessDeniedError):
    return JSONResponse(
        status_code=403,
        content={"error_code": exc.code, "message": exc.message}
    )
# ✅ Import and include routers
from app.routers import (
    # Governance-related routers
    user, project, env, user_role, project_config,
    feature_names, feature_role_access_matrix, db_defination_table,
    user_app_matrix, workflows, governance_delete_logs,

    # Orchestration-related routers
    tdm_tool, orchestration_access_matrix, tdm_tool_services_field,
    genrocket_services_details, genrocket_services_execution_details,
    orchestration_delete_logs, execution_method_router,
    db_orchestration_workflows, db_orchestration_access_matrix,
    db_orchestration_execution_logs, db_workflow_deleted_logs,

    # Common/Utility routers
    api_sequence, workflow_apis_details, application_access_matrix_,
    api_mappings, excel_mappings, execution_logs, aa_workflow_deleted_logs_,
    project_mi_view, project_mi_view_SDG, project_mi_view_DB,
    sql_template, sequence_mappings, runtime_logs
)

# ✅ Register routers
app.include_router(user.router)
app.include_router(project.router)
app.include_router(env.router)
app.include_router(user_role.router)
app.include_router(project_config.router)
app.include_router(feature_names.router)
app.include_router(feature_role_access_matrix.router)
app.include_router(db_defination_table.router)
app.include_router(user_app_matrix.router)
app.include_router(governance_delete_logs.router)

app.include_router(tdm_tool.router)
app.include_router(orchestration_access_matrix.router)
app.include_router(tdm_tool_services_field.router)
app.include_router(genrocket_services_details.router)
app.include_router(genrocket_services_execution_details.router)
app.include_router(orchestration_delete_logs.router)
app.include_router(execution_method_router.router, prefix="/api", tags=["GenRocket Execution"])
app.include_router(db_orchestration_workflows.router)
app.include_router(db_orchestration_access_matrix.router)
app.include_router(db_orchestration_execution_logs.router)
app.include_router(db_workflow_deleted_logs.router)

app.include_router(api_sequence.router)
app.include_router(workflow_apis_details.router)
app.include_router(application_access_matrix_.router)
app.include_router(api_mappings.router)
app.include_router(excel_mappings.router)
app.include_router(execution_logs.router)
app.include_router(aa_workflow_deleted_logs_.router)
app.include_router(project_mi_view.router)
app.include_router(project_mi_view_SDG.router)
app.include_router(project_mi_view_DB.router)
app.include_router(sql_template.router)
app.include_router(sequence_mappings.router)
app.include_router(runtime_logs.router)
app.include_router(environment_instance.router)
app.include_router(status.router)
# ✅ No extra prefix here
app.include_router(auth.router)

#app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# ✅ Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to Data360 Governance & Orchestration API!"}
