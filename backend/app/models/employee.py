"""
HRPulse — SQLAlchemy ORM Models
All database table definitions for the HR platform.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)

from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# USER MODEL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EMPLOYEE MODEL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class Employee(Base):
    __tablename__ = "employees"

    id = Column(String(50), primary_key=True)  # EMP-0001 format
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    department = Column(String(100), nullable=False, index=True)
    job_role = Column(String(100), nullable=False)
    tenure_years = Column(Integer, default=0)
    salary = Column(Integer, default=0)
    salary_hike_percent = Column(Float, default=0.0)
    monthly_income = Column(Float, default=0.0)
    distance_from_home = Column(Integer, default=0)
    job_satisfaction = Column(Integer, default=3)
    work_life_balance = Column(Integer, default=3)
    overtime = Column(String(10), default="No")
    performance_rating = Column(Integer, default=3)
    num_companies_worked = Column(Integer, default=0)
    years_at_company = Column(Integer, default=0)
    years_since_last_promotion = Column(Integer, default=0)
    manager_rating = Column(Integer, default=3)
    absences_per_year = Column(Integer, default=0)
    attrition = Column(String(10), default="No")
    created_at = Column(DateTime(timezone=True), default=utcnow)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# JOB DESCRIPTION MODEL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False, index=True)
    required_skills = Column(Text, nullable=True)  # JSON array
    nice_to_have_skills = Column(Text, nullable=True)  # JSON array
    interview_questions = Column(Text, nullable=True) # JSON array
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CANDIDATE / RESUME MODEL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    job_id = Column(String(50), nullable=True) # link to job description
    skills = Column(Text, nullable=True)  # JSON array
    experience_years = Column(Integer, default=0)
    education = Column(String(500), nullable=True)
    previous_roles = Column(Text, nullable=True)  # JSON array
    resume_text = Column(Text, nullable=True)
    ai_evaluation = Column(Text, nullable=True) # Storing the "Should we hire" LLM result
    created_at = Column(DateTime(timezone=True), default=utcnow)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# UPLOAD LOG MODEL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class UploadLog(Base):
    __tablename__ = "upload_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # csv, pdf, txt
    file_size = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    records_processed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    uploaded_by = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
