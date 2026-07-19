from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import inspect, text
from app.database import engine, Base
from app.config import settings
from app.routers import category, auth, course, roadmap_step, resource, enrollment, user_progress, bookmark, note, dashboard, analytics, search, roadmap, resources_cache

# Initialize the database tables that do not exist (e.g. categories)
Base.metadata.create_all(bind=engine)

def ensure_database_compatibility() -> None:
    """
    Applies tiny additive compatibility fixes for projects without Alembic migrations.
    """
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "password_hash" not in user_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))

ensure_database_compatibility()

app = FastAPI(
    title="LearnHub - Student Learning Platform Backend",
    description="Production-ready REST API backend for managing categories, courses, roadmaps, enrollments, bookmarks, progress and notes.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
allowed_origins = [origin.strip() for origin in settings.FRONTEND_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(category.router, prefix="/api/v1")
app.include_router(course.router, prefix="/api/v1")
app.include_router(roadmap_step.router, prefix="/api/v1")
app.include_router(resource.router, prefix="/api/v1")
app.include_router(enrollment.router, prefix="/api/v1")
app.include_router(user_progress.router, prefix="/api/v1")
app.include_router(bookmark.router, prefix="/api/v1")
app.include_router(note.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(roadmap.router, prefix="/api/v1")
app.include_router(resources_cache.router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to LearnHub API. Visit /docs for documentation.",
        "status": "healthy"
    }

# Exception Handlers
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handles request validation errors (e.g. invalid Pydantic input).
    Ensures non-serializable exception objects in context are converted to strings.
    """
    safe_errors = []
    for error in exc.errors():
        err_dict = dict(error)
        if "ctx" in err_dict and isinstance(err_dict["ctx"], dict):
            ctx_dict = dict(err_dict["ctx"])
            for key, val in ctx_dict.items():
                if isinstance(val, Exception):
                    ctx_dict[key] = str(val)
            err_dict["ctx"] = ctx_dict
        safe_errors.append(err_dict)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": safe_errors
        }
    )

@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handles standard HTTPExceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail
        }
    )

@app.exception_handler(Exception)
def general_exception_handler(request: Request, exc: Exception):
    """
    Catch-all for unhandled server exceptions.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": str(exc)
        }
    )

@app.on_event("startup")
async def startup_event():
    """
    Spawns background tasks for cache cleaning, cache refreshing, and pre-calculated trending topics.
    """
    import asyncio
    from app.services.background_jobs import clean_expired_cache_job, refresh_stale_cache_job, precalculate_trending_job
    
    # Spawn non-blocking background tasks
    asyncio.create_task(clean_expired_cache_job())
    asyncio.create_task(refresh_stale_cache_job())
    asyncio.create_task(precalculate_trending_job())
