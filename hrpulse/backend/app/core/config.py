"""
HRPulse — Application Configuration
Centralized settings loaded from environment variables with sensible defaults.
"""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings — values loaded from .env or environment variables."""

    # ── Application ───────────────────────────
    APP_NAME: str = "HRPulse"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ── Database ──────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://hrpulse:hrpulse_secret@localhost:5432/hrpulse_db"
    DATABASE_URL_SYNC: str = "postgresql://hrpulse:hrpulse_secret@localhost:5432/hrpulse_db"

    # ── Redis ─────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Celery ────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── JWT Authentication ────────────────────
    JWT_SECRET_KEY: str = "hrpulse-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ──────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # ── Ollama (Local LLM) ───────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"

    # ── MLflow ────────────────────────────────
    MLFLOW_TRACKING_URI: str = "http://localhost:5001"

    # ── File Paths ────────────────────────────
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    ML_MODELS_DIR: Path = BASE_DIR / "ml_models"
    UPLOADS_DIR: Path = BASE_DIR / "uploads"

    # ── Azure (for cloud deployment) ──────────
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton settings instance
settings = Settings()

# Ensure directories exist
settings.ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
