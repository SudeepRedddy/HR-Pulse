"""
HRPulse — Celery Application
Async task queue for ML model training and inference jobs.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "hrpulse",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task
    task_soft_time_limit=540,  # soft limit at 9 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Auto-discover tasks in app.services
celery_app.autodiscover_tasks(["app.services"])
