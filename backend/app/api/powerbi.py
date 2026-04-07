from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict

from app.core.database import get_db
from app.models.employee import Employee, JobDescription, Candidate

router = APIRouter(prefix="/powerbi", tags=["Power BI"])

@router.get("/summary")
async def get_analytics_summary(db: AsyncSession = Depends(get_db)):
    """Analytics summary for interactive frontend Dashboard."""
    
    # 1. Total Employees
    emp_count = await db.execute(select(func.count(Employee.id)))
    total_employees = emp_count.scalar() or 0
    
    # 2. Open Roles
    jobs_count = await db.execute(select(func.count(JobDescription.id)))
    open_roles = jobs_count.scalar() or 0
    
    # 3. Total Candidates
    cands_count = await db.execute(select(func.count(Candidate.id)))
    total_candidates = cands_count.scalar() or 0
    
    # 4. Department Breakdown
    dept_breakdown = defaultdict(int)
    employees_result = await db.execute(select(Employee.department, Employee.salary, Employee.attrition, Employee.job_satisfaction))
    all_rows = employees_result.all()
    
    total_at_risk = 0
    total_satisfaction = 0
    
    salary_distribution = {
        "< $50k": 0,
        "$50k - $80k": 0,
        "$80k - $120k": 0,
        "$120k+": 0
    }
    
    for dept, sal, attrition, satisfaction in all_rows:
        dept_breakdown[dept] += 1
        
        # Salary bins
        sal = sal or 0
        if sal < 50000:
            salary_distribution["< $50k"] += 1
        elif sal < 80000:
            salary_distribution["$50k - $80k"] += 1
        elif sal < 120000:
            salary_distribution["$80k - $120k"] += 1
        else:
            salary_distribution["$120k+"] += 1
        
        # Attrition count
        if attrition == "Yes":
            total_at_risk += 1
        
        # Satisfaction sum
        total_satisfaction += (satisfaction or 3)

    attrition_rate = round((total_at_risk / max(total_employees, 1)) * 100, 1)
    avg_satisfaction = round(total_satisfaction / max(total_employees, 1), 1)

    return {
        "total_employees": total_employees,
        "open_roles": open_roles,
        "total_candidates": total_candidates,
        "attrition_rate": attrition_rate,
        "avg_satisfaction": avg_satisfaction,
        "department_breakdown": dict(dept_breakdown),
        "salary_distribution": salary_distribution
    }
