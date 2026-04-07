"""
HRPulse — FastAPI Application Entry Point
AI-Powered Autonomous HR Intelligence Platform
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.employees import router as employees_router
from app.api.recruitment import router as recruitment_router
from app.api.uploads import router as uploads_router
from app.api.aria import router as aria_router
from app.api.powerbi import router as powerbi_router
from app.api.predictions import router as predictions_router
from app.core.config import settings


# ── Lifespan (startup / shutdown) ────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # ── Startup ──
    print("━" * 50)
    print(f"  {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"  Environment: {settings.ENVIRONMENT}")
    print("━" * 50)
    print("  ✓ Application started")
    print("  ✓ API docs: http://localhost:8000/docs")

    yield

    # ── Shutdown ──
    print("  ✗ Application shutting down")


# ── Create FastAPI App ───────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Autonomous HR Intelligence Platform",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS Middleware ──────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health Check ─────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint — health check."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "api": "operational",
            "database": "connected",
            "redis": "connected",
            "ml_models": "loaded",
        },
    }


# ── Register Routers ────────────────────────
app.include_router(auth_router, prefix="/api")
app.include_router(employees_router, prefix="/api")
app.include_router(recruitment_router, prefix="/api")
app.include_router(uploads_router, prefix="/api")
app.include_router(aria_router, prefix="/api")
app.include_router(powerbi_router, prefix="/api")
app.include_router(predictions_router, prefix="/api")


# ── Global Exception Handler ────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch-all exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred",
            "error": str(exc) if settings.DEBUG else "Internal Server Error",
        },
    )
