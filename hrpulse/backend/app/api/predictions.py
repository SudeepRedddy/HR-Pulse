"""
HRPulse — Predictions API Routes
Workforce-level predictive analytics computed from employee metrics.

GET /api/predictions/workforce-forecast
GET /api/predictions/retention-risk
GET /api/predictions/department-health
GET /api/predictions/promotion-readiness
GET /api/predictions/salary-insights
"""

from collections import defaultdict
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.employee import Employee

router = APIRouter(prefix="/predictions", tags=["Predictions"])


def _compute_risk_score(emp) -> float:
    """Compute individual attrition risk score (0.0–1.0) from employee metrics."""
    score = 0.0
    if emp.job_satisfaction <= 2:
        score += 0.25
    if emp.work_life_balance <= 2:
        score += 0.15
    if emp.overtime == "Yes":
        score += 0.12
    if emp.salary_hike_percent < 12:
        score += 0.08
    if emp.years_since_last_promotion >= 4:
        score += 0.15
    if emp.manager_rating <= 2:
        score += 0.12
    if emp.distance_from_home > 25:
        score += 0.06
    if emp.num_companies_worked >= 5:
        score += 0.08
    return min(score, 1.0)


def _compute_performance_score(emp) -> float:
    """Compute weighted performance index (0–100)."""
    score = 0.0
    score += (emp.performance_rating / 4.0) * 30
    score += (emp.job_satisfaction / 4.0) * 20
    score += (emp.work_life_balance / 4.0) * 15
    score += (emp.manager_rating / 5.0) * 15
    score += min(emp.tenure_years / 10.0, 1.0) * 10
    score -= (emp.absences_per_year / 20.0) * 5
    ot_penalty = 5 if emp.overtime == "Yes" else 0
    score -= ot_penalty
    return max(0, min(100, score))


@router.get("/workforce-forecast")
async def workforce_forecast(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Predict workforce trends for the next quarter.
    Estimates attrition forecast, hiring needs, and department-level risk.
    """
    result = await db.execute(select(Employee))
    employees = result.scalars().all()

    total = len(employees)
    if total == 0:
        return {"total_employees": 0, "message": "No employees in the system."}

    # Compute risk for all
    risk_scores = [_compute_risk_score(e) for e in employees]
    high_risk_count = sum(1 for s in risk_scores if s >= 0.6)
    medium_risk_count = sum(1 for s in risk_scores if 0.3 <= s < 0.6)
    avg_risk = sum(risk_scores) / len(risk_scores)

    # Predict next-quarter attrition (employees likely to leave)
    predicted_exits = sum(1 for s in risk_scores if s >= 0.5)
    attrition_forecast_pct = round((predicted_exits / total) * 100, 1)

    # Department risk heatmap
    dept_risk = defaultdict(list)
    for emp, score in zip(employees, risk_scores):
        dept_risk[emp.department].append(score)

    dept_heatmap = {}
    for dept, scores in dept_risk.items():
        avg = sum(scores) / len(scores)
        dept_heatmap[dept] = {
            "avg_risk": round(avg * 100, 1),
            "headcount": len(scores),
            "high_risk_count": sum(1 for s in scores if s >= 0.6),
            "risk_level": "High" if avg >= 0.5 else "Medium" if avg >= 0.3 else "Low",
        }

    # Current attrition count
    current_attrition = sum(1 for e in employees if e.attrition == "Yes")

    return {
        "total_employees": total,
        "current_attrition_count": current_attrition,
        "current_attrition_rate": round((current_attrition / total) * 100, 1),
        "predicted_exits_next_quarter": predicted_exits,
        "attrition_forecast_pct": attrition_forecast_pct,
        "recommended_hires": max(predicted_exits + 5, 10),
        "avg_risk_score": round(avg_risk * 100, 1),
        "high_risk_employees": high_risk_count,
        "medium_risk_employees": medium_risk_count,
        "department_heatmap": dept_heatmap,
    }


@router.get("/retention-risk")
async def retention_risk(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Top employees most likely to leave, ranked by risk score.
    Returns the top 15 with contributing factors.
    """
    result = await db.execute(select(Employee))
    employees = result.scalars().all()

    risk_list = []
    for emp in employees:
        score = _compute_risk_score(emp)
        factors = []
        if emp.job_satisfaction <= 2:
            factors.append("Low job satisfaction")
        if emp.work_life_balance <= 2:
            factors.append("Poor work-life balance")
        if emp.overtime == "Yes":
            factors.append("Regular overtime")
        if emp.salary_hike_percent < 12:
            factors.append("Below-average salary growth")
        if emp.years_since_last_promotion >= 4:
            factors.append("Stalled career progression")
        if emp.manager_rating <= 2:
            factors.append("Low manager alignment")
        if emp.distance_from_home > 25:
            factors.append("Long commute")
        if emp.num_companies_worked >= 5:
            factors.append("Frequent job changes")

        risk_list.append({
            "employee_id": emp.id,
            "name": emp.name,
            "department": emp.department,
            "job_role": emp.job_role,
            "tenure_years": emp.tenure_years,
            "risk_score": round(score * 100, 1),
            "risk_level": "High" if score >= 0.6 else "Medium" if score >= 0.3 else "Low",
            "factors": factors,
        })

    # Sort by risk descending
    risk_list.sort(key=lambda x: x["risk_score"], reverse=True)

    return {
        "top_at_risk": risk_list[:15],
        "total_high_risk": sum(1 for r in risk_list if r["risk_level"] == "High"),
        "total_medium_risk": sum(1 for r in risk_list if r["risk_level"] == "Medium"),
        "total_low_risk": sum(1 for r in risk_list if r["risk_level"] == "Low"),
    }


@router.get("/department-health")
async def department_health(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Per-department health scorecard.
    Aggregates satisfaction, performance, overtime, and attrition metrics.
    """
    result = await db.execute(select(Employee))
    employees = result.scalars().all()

    dept_data = defaultdict(lambda: {
        "count": 0,
        "satisfaction_sum": 0,
        "performance_sum": 0,
        "wlb_sum": 0,
        "overtime_count": 0,
        "attrition_count": 0,
        "salary_sum": 0,
        "tenure_sum": 0,
        "manager_rating_sum": 0,
    })

    for emp in employees:
        d = dept_data[emp.department]
        d["count"] += 1
        d["satisfaction_sum"] += emp.job_satisfaction
        d["performance_sum"] += emp.performance_rating
        d["wlb_sum"] += emp.work_life_balance
        d["overtime_count"] += 1 if emp.overtime == "Yes" else 0
        d["attrition_count"] += 1 if emp.attrition == "Yes" else 0
        d["salary_sum"] += emp.salary
        d["tenure_sum"] += emp.tenure_years
        d["manager_rating_sum"] += emp.manager_rating

    departments = []
    for dept, d in dept_data.items():
        n = d["count"]
        avg_satisfaction = round(d["satisfaction_sum"] / n, 2)
        avg_performance = round(d["performance_sum"] / n, 2)
        avg_wlb = round(d["wlb_sum"] / n, 2)
        overtime_pct = round((d["overtime_count"] / n) * 100, 1)
        attrition_pct = round((d["attrition_count"] / n) * 100, 1)
        avg_salary = round(d["salary_sum"] / n)
        avg_tenure = round(d["tenure_sum"] / n, 1)
        avg_manager = round(d["manager_rating_sum"] / n, 2)

        # Health score: weighted combination (0-100)
        health = 0.0
        health += (avg_satisfaction / 4.0) * 30
        health += (avg_performance / 4.0) * 25
        health += (avg_wlb / 4.0) * 20
        health -= (overtime_pct / 100.0) * 10
        health -= (attrition_pct / 100.0) * 15
        health = max(0, min(100, health))

        departments.append({
            "department": dept,
            "headcount": n,
            "health_score": round(health, 1),
            "avg_satisfaction": avg_satisfaction,
            "avg_performance": avg_performance,
            "avg_work_life_balance": avg_wlb,
            "overtime_pct": overtime_pct,
            "attrition_pct": attrition_pct,
            "avg_salary": avg_salary,
            "avg_tenure": avg_tenure,
            "avg_manager_rating": avg_manager,
        })

    # Sort by health score descending
    departments.sort(key=lambda x: x["health_score"], reverse=True)

    return {"departments": departments}


@router.get("/promotion-readiness")
async def promotion_readiness(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Identify employees ready for promotion based on tenure,
    performance, manager rating, and years since last promotion.
    """
    result = await db.execute(select(Employee))
    employees = result.scalars().all()

    candidates = []
    for emp in employees:
        # Promotion readiness score (0–100)
        readiness = 0.0
        readiness += min(emp.tenure_years / 5.0, 1.0) * 25  # Tenure weight
        readiness += (emp.performance_rating / 4.0) * 30  # Performance weight
        readiness += (emp.manager_rating / 5.0) * 20  # Manager endorsement
        readiness += min(emp.years_since_last_promotion / 3.0, 1.0) * 15  # Overdue factor
        readiness += (emp.job_satisfaction / 4.0) * 10  # Engagement
        readiness = max(0, min(100, readiness))

        if readiness >= 65:
            reasons = []
            if emp.performance_rating >= 3:
                reasons.append("Strong performance rating")
            if emp.tenure_years >= 3:
                reasons.append(f"{emp.tenure_years}+ years tenure")
            if emp.manager_rating >= 4:
                reasons.append("High manager endorsement")
            if emp.years_since_last_promotion >= 3:
                reasons.append(f"Overdue by {emp.years_since_last_promotion} years")

            candidates.append({
                "employee_id": emp.id,
                "name": emp.name,
                "department": emp.department,
                "job_role": emp.job_role,
                "tenure_years": emp.tenure_years,
                "performance_rating": emp.performance_rating,
                "manager_rating": emp.manager_rating,
                "years_since_promotion": emp.years_since_last_promotion,
                "readiness_score": round(readiness, 1),
                "reasons": reasons,
            })

    candidates.sort(key=lambda x: x["readiness_score"], reverse=True)

    return {
        "promotion_candidates": candidates[:20],
        "total_ready": len(candidates),
    }


@router.get("/salary-insights")
async def salary_insights(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Salary equity analysis: department averages, underpaid detection,
    and compensation distribution.
    """
    result = await db.execute(select(Employee))
    employees = result.scalars().all()

    if not employees:
        return {"message": "No employees found."}

    all_salaries = [e.salary for e in employees]
    overall_avg = sum(all_salaries) / len(all_salaries)
    overall_median = sorted(all_salaries)[len(all_salaries) // 2]

    # Department averages
    dept_salaries = defaultdict(list)
    for emp in employees:
        dept_salaries[emp.department].append(emp.salary)

    dept_analysis = {}
    for dept, salaries in dept_salaries.items():
        avg = sum(salaries) / len(salaries)
        dept_analysis[dept] = {
            "avg_salary": round(avg),
            "min_salary": min(salaries),
            "max_salary": max(salaries),
            "headcount": len(salaries),
            "vs_company_avg": round(((avg - overall_avg) / overall_avg) * 100, 1),
        }

    # Underpaid employees: >20% below their department avg + high performance
    underpaid = []
    for emp in employees:
        dept_avg = sum(dept_salaries[emp.department]) / len(dept_salaries[emp.department])
        gap_pct = ((dept_avg - emp.salary) / dept_avg) * 100
        if gap_pct > 20 and emp.performance_rating >= 3:
            underpaid.append({
                "employee_id": emp.id,
                "name": emp.name,
                "department": emp.department,
                "job_role": emp.job_role,
                "salary": emp.salary,
                "dept_avg": round(dept_avg),
                "gap_pct": round(gap_pct, 1),
                "performance_rating": emp.performance_rating,
            })

    underpaid.sort(key=lambda x: x["gap_pct"], reverse=True)

    # Salary brackets
    brackets = {"< $50k": 0, "$50k–$80k": 0, "$80k–$120k": 0, "$120k+": 0}
    for s in all_salaries:
        if s < 50000:
            brackets["< $50k"] += 1
        elif s < 80000:
            brackets["$50k–$80k"] += 1
        elif s < 120000:
            brackets["$80k–$120k"] += 1
        else:
            brackets["$120k+"] += 1

    return {
        "overall_avg_salary": round(overall_avg),
        "overall_median_salary": overall_median,
        "total_employees": len(employees),
        "department_analysis": dept_analysis,
        "underpaid_employees": underpaid[:10],
        "salary_brackets": brackets,
    }
