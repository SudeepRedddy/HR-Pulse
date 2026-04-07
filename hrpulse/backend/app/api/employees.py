"""
HRPulse — Employees API Routes
GET  /api/employees          (paginated, filterable)
POST /api/employees          (create new)
GET  /api/employees/{id}
GET  /api/employees/{id}/performance
GET  /api/employees/{id}/risk
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.employee import Employee
from app.schemas.schemas import EmployeeBase, EmployeeListResponse, EmployeeResponse, EmployeePerformanceEvaluation

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("", response_model=EmployeeListResponse)
async def list_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    department: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all employees with pagination and filtering."""
    query = select(Employee)

    if department:
        query = query.where(Employee.department == department)
    if search:
        query = query.where(
            Employee.name.ilike(f"%{search}%") | Employee.job_role.ilike(f"%{search}%")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Employee.id)

    result = await db.execute(query)
    employees = result.scalars().all()

    return EmployeeListResponse(
        employees=[EmployeeResponse.model_validate(emp) for emp in employees],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=EmployeeResponse)
async def create_employee(
    request: EmployeeBase,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new employee record."""
    import uuid
    emp_data = request.model_dump()
    if "id" not in emp_data or not emp_data.get("id"):
        emp_data["id"] = f"EMP-{str(uuid.uuid4())[:4].upper()}"
    new_employee = Employee(**emp_data)
    db.add(new_employee)
    await db.commit()
    await db.refresh(new_employee)
    return EmployeeResponse.model_validate(new_employee)


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a single employee by ID."""
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return EmployeeResponse.model_validate(employee)


@router.get("/{employee_id}/performance", response_model=EmployeePerformanceEvaluation)
async def get_employee_performance(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    ML Performance Predictor — generates an actionable English evaluation
    based on the employee's metrics. Uses a weighted scoring model.
    """
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # ── Weighted Performance Score ──────────────────
    # Simulates a trained XGBoost/Random Forest model output
    score = 0.0
    score += (employee.performance_rating / 4.0) * 30   # 30% weight
    score += (employee.job_satisfaction / 4.0) * 20      # 20% weight
    score += (employee.work_life_balance / 4.0) * 15     # 15% weight
    score += (employee.manager_rating / 5.0) * 15        # 15% weight
    score += min(employee.tenure_years / 10.0, 1.0) * 10 # 10% weight
    score -= (employee.absences_per_year / 20.0) * 5     # -5% penalty
    ot_penalty = 5 if employee.overtime == "Yes" else 0
    score -= ot_penalty                                   # -5% OT penalty
    score = max(0, min(100, score))

    # ── Generate Natural Language Summary ──────────
    tier = ""
    recommendation = ""

    if score >= 75:
        tier = "Top Performer"
        recommendation = (
            f"Based on our predictive analysis, {employee.name} scores {score:.0f}/100 on the "
            f"HRPulse Performance Index. They are identified as a **Top Performer** within the "
            f"{employee.department} division. With {employee.tenure_years} years of tenure and a "
            f"manager rating of {employee.manager_rating}/5, they are primed for a leadership track. "
            f"Recommendation: Fast-track for promotion review and include in the next succession planning cycle."
        )
    elif score >= 50:
        tier = "Steady Contributor"
        recommendation = (
            f"{employee.name} scores {score:.0f}/100 on the HRPulse Performance Index, placing them in the "
            f"**Steady Contributor** tier for {employee.department}. Their satisfaction level of "
            f"{employee.job_satisfaction}/4 and work-life balance of {employee.work_life_balance}/4 suggest stable engagement. "
            f"Recommendation: Consider targeted upskilling opportunities and a mid-cycle performance check-in to explore growth."
        )
    else:
        tier = "Needs Attention"
        factors = []
        if employee.job_satisfaction <= 2:
            factors.append("low job satisfaction")
        if employee.work_life_balance <= 2:
            factors.append("poor work-life balance")
        if employee.overtime == "Yes":
            factors.append("consistent overtime")
        if employee.absences_per_year > 10:
            factors.append(f"high absenteeism ({employee.absences_per_year} days/year)")
        if employee.manager_rating <= 2:
            factors.append("low manager alignment")

        factor_str = ", ".join(factors) if factors else "multiple compounding metrics"
        recommendation = (
            f"Alert: {employee.name} scores {score:.0f}/100 on the HRPulse Performance Index, flagged as "
            f"**Needs Attention**. Contributing factors include {factor_str}. "
            f"Recommendation: Schedule a confidential 1-on-1 within 5 business days. "
            f"Review workload distribution and explore whether a role adjustment or mentorship pairing could help."
        )

    return EmployeePerformanceEvaluation(
        employee_id=employee_id,
        performance_summary=recommendation
    )


@router.get("/{employee_id}/risk")
async def get_employee_risk(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Attrition Risk Predictor — returns a risk level and contributing factors.
    Simulates a logistic regression / XGBoost classifier output.
    """
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    risk_score = 0.0
    factors = []

    if employee.job_satisfaction <= 2:
        risk_score += 0.25
        factors.append("Low job satisfaction")
    if employee.work_life_balance <= 2:
        risk_score += 0.15
        factors.append("Poor work-life balance")
    if employee.overtime == "Yes":
        risk_score += 0.12
        factors.append("Regular overtime")
    if employee.salary_hike_percent < 12:
        risk_score += 0.08
        factors.append("Below-average salary growth")
    if employee.years_since_last_promotion >= 4:
        risk_score += 0.15
        factors.append("Stalled career progression")
    if employee.manager_rating <= 2:
        risk_score += 0.12
        factors.append("Low manager alignment")
    if employee.distance_from_home > 25:
        risk_score += 0.06
        factors.append("Long commute distance")
    if employee.num_companies_worked >= 5:
        risk_score += 0.08
        factors.append("Frequent job changes")

    risk_score = min(risk_score, 1.0)
    risk_pct = round(risk_score * 100, 1)

    if risk_pct >= 60:
        level = "High"
    elif risk_pct >= 30:
        level = "Medium"
    else:
        level = "Low"

    return {
        "employee_id": employee_id,
        "risk_level": level,
        "risk_percentage": risk_pct,
        "contributing_factors": factors,
        "recommendation": f"{'Immediate intervention recommended.' if level == 'High' else 'Monitor during next review cycle.' if level == 'Medium' else 'No action required.'}"
    }
