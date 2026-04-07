"""
HRPulse — Pydantic Schemas
Request/response validation models for all API endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AUTH SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EMPLOYEE SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class EmployeeBase(BaseModel):
    name: str
    age: int
    gender: str
    department: str
    job_role: str
    tenure_years: int = 0
    salary: int = 0
    salary_hike_percent: float = 0.0
    monthly_income: float = 0.0
    distance_from_home: int = 0
    job_satisfaction: int = 3
    work_life_balance: int = 3
    overtime: str = "No"
    performance_rating: int = 3
    num_companies_worked: int = 0
    years_at_company: int = 0
    years_since_last_promotion: int = 0
    manager_rating: int = 3
    absences_per_year: int = 0
    attrition: str = "No"


class EmployeeResponse(EmployeeBase):
    id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    employees: List[EmployeeResponse]
    total: int
    page: int
    page_size: int


class EmployeePerformanceEvaluation(BaseModel):
    employee_id: str
    performance_summary: str


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DASHBOARD SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class DashboardSummary(BaseModel):
    total_employees: int
    open_roles: int
    total_candidates: int
    department_breakdown: Dict[str, int]
    salary_distribution: Dict[str, float]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RECRUITMENT SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class JobDescriptionBase(BaseModel):
    title: str
    department: str
    required_skills: Optional[str] = None
    nice_to_have_skills: Optional[str] = None
    interview_questions: Optional[str] = None
    description: Optional[str] = None

class JobDescriptionResponse(JobDescriptionBase):
    id: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CandidateBase(BaseModel):
    name: str
    job_id: Optional[str] = None
    skills: Optional[str] = None
    experience_years: int = 0
    education: Optional[str] = None
    previous_roles: Optional[str] = None
    resume_text: Optional[str] = None

class CandidateResponse(CandidateBase):
    id: str
    ai_evaluation: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# UPLOAD SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class UploadResponse(BaseModel):
    filename: str
    file_type: str
    file_size: int
    status: str
    message: str = ""
