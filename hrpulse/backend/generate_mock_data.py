"""
HRPulse — Mock Data Generator
Generates employees.csv, feedback_surveys.csv, and performance_history.csv
with realistic correlations and distributions.

Usage: python generate_mock_data.py
Output: All CSV files are written to backend/data/
"""

import csv
import json
import os
import random
import sys
from pathlib import Path

# ── Seed for reproducibility ─────────────────────────────────
random.seed(42)

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEPARTMENTS = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations"]

JOB_ROLES = {
    "Engineering": ["Software Engineer", "Senior Software Engineer", "Tech Lead", "DevOps Engineer", "QA Engineer", "Data Engineer"],
    "Sales": ["Sales Executive", "Account Manager", "Sales Manager", "Business Development Rep", "Regional Sales Lead", "Sales Analyst"],
    "Marketing": ["Marketing Specialist", "Content Strategist", "Digital Marketing Manager", "SEO Analyst", "Brand Manager", "Marketing Coordinator"],
    "HR": ["HR Generalist", "HR Business Partner", "Recruiter", "Talent Acquisition Lead", "People Ops Specialist", "Compensation Analyst"],
    "Finance": ["Financial Analyst", "Senior Accountant", "Finance Manager", "Budget Analyst", "Treasury Analyst", "Audit Associate"],
    "Operations": ["Operations Coordinator", "Process Manager", "Operations Analyst", "Supply Chain Lead", "Facilities Manager", "Operations Manager"],
}

FIRST_NAMES_MALE = [
    "Aarav", "Arjun", "Rahul", "Vikram", "Suresh", "Amit", "Rohan", "Karthik", "Deepak", "Anil",
    "James", "Robert", "Michael", "David", "Daniel", "Alexander", "Marcus", "Thomas", "William", "Joseph",
    "Ravi", "Sanjay", "Manoj", "Pranav", "Nikhil", "Harsh", "Gaurav", "Varun", "Akash", "Hemant",
    "Christopher", "Andrew", "Benjamin", "Samuel", "Nathan", "Ethan", "Ryan", "Kevin", "Brian", "Patrick",
]

FIRST_NAMES_FEMALE = [
    "Priya", "Neha", "Kavitha", "Ananya", "Sneha", "Divya", "Pooja", "Ritu", "Meera", "Swati",
    "Sarah", "Emily", "Lisa", "Jessica", "Jennifer", "Amanda", "Rachel", "Stephanie", "Nicole", "Megan",
    "Aisha", "Fatima", "Shreya", "Tanvi", "Isha", "Aditi", "Nupur", "Sanya", "Kriti", "Disha",
    "Michelle", "Laura", "Angela", "Christina", "Rebecca", "Katherine", "Diana", "Monica", "Sophia", "Emma",
]

LAST_NAMES = [
    "Sharma", "Patel", "Kumar", "Singh", "Reddy", "Mehta", "Gupta", "Nair", "Iyer", "Deshmukh",
    "Johnson", "Williams", "Thompson", "Garcia", "Wilson", "Anderson", "Taylor", "Brown", "Davis", "Miller",
    "Chen", "Kim", "Lee", "Park", "Wang", "Tanaka", "Nakamura", "Sato", "Khan", "Ali",
    "Rodriguez", "Martinez", "Lopez", "Fernandez", "Torres", "Hernandez", "Morales", "Reyes", "Cruz", "Santos",
    "Turner", "Harris", "Clark", "Lewis", "Walker", "Hall", "Young", "King", "Wright", "Scott",
]

# ── Feedback templates ────────────────────────────────────
POSITIVE_FEEDBACK = [
    "I really enjoy working here. The team is supportive and the projects are interesting. I feel valued and my contributions are recognized by my manager.",
    "Great work environment with excellent learning opportunities. The company invests in our growth and the work-life balance has been phenomenal this quarter.",
    "My manager is incredibly supportive and provides clear direction. The team collaboration is excellent and I feel motivated to come to work every day.",
    "The recent changes to our workflow have been very positive. I appreciate the transparency from leadership and the new tools we have been provided.",
    "I am proud to be part of this organization. The culture of innovation is inspiring and I have had the opportunity to work on meaningful projects that make a real impact.",
    "Excellent quarter overall. My career development has been a priority for my manager and I have received valuable mentoring. The compensation package is competitive.",
    "The flexibility offered by the remote work policy has greatly improved my productivity and job satisfaction. I feel trusted by my team and empowered to make decisions.",
    "I appreciate the recent training programs. They have helped me develop new skills that are directly applicable to my role. The learning culture here is outstanding.",
    "Working with my cross-functional team has been a highlight this quarter. The projects are challenging in the best way and the team celebrates wins together.",
    "The company culture is exactly what I was looking for. Respectful, innovative, and growth-oriented. I would recommend this workplace to anyone in my network.",
    "My role continues to challenge me in positive ways. I have autonomy over my projects and the leadership team genuinely listens to feedback from all levels.",
    "This quarter has been my best yet. The new project I was assigned to aligns perfectly with my career goals and I have received excellent peer support throughout.",
    "The onboarding process was smooth and well-organized. I felt welcomed from day one and had all the resources I needed to start contributing quickly.",
    "I am grateful for the mentorship I have received this quarter. My senior colleagues are generous with their time and knowledge, which has accelerated my growth.",
    "The quarterly town halls have improved communication significantly. I feel informed about company direction and my role in the bigger picture.",
]

NEUTRAL_FEEDBACK = [
    "Overall things are going fine. Some processes could be improved but nothing major. The workload has been manageable and meetings are at a reasonable level.",
    "The quarter has been average. No major issues but also no standout moments. I think we could improve our project management tools and meeting efficiency.",
    "Work has been steady this quarter. I would appreciate more clarity on career progression paths. The day-to-day responsibilities are clear but long-term growth is uncertain.",
    "Things are okay. The work itself is interesting but the communication between departments could be better. Sometimes priorities shift without clear explanation.",
    "My role is what I expected. I do not have strong complaints but I think the performance review process could be more frequent and more actionable.",
    "The team dynamics are acceptable. We get along well but could collaborate more effectively. I think we need better documentation of our processes and decisions.",
    "I am satisfied with my current position but feel somewhat stagnant. I would like more challenging assignments or opportunities to learn adjacent skills.",
    "This quarter was a mix of positive and challenging experiences. The project deadline was tight but we managed. Better planning upfront would have reduced stress.",
    "The workplace is fine overall. Compensation is fair for the market. I think the company could invest more in social events and team building activities.",
    "My feedback about the new software tools is mixed. Some have improved our workflow while others have added unnecessary complexity. A review would be beneficial.",
]

NEGATIVE_FEEDBACK = [
    "I am feeling overwhelmed with the current workload. The overtime expectations are unreasonable and it is affecting my personal life. I need better work-life balance.",
    "Communication from management has been poor this quarter. Decisions are made without consulting the team and priorities change weekly. It is frustrating and demotivating.",
    "I have not received a meaningful raise in two years despite taking on significantly more responsibilities. I feel undervalued and am considering my options elsewhere.",
    "The recent organizational changes have created confusion about roles and responsibilities. Morale on the team is low and several colleagues have already started looking for new positions.",
    "My manager rarely provides feedback and is often unavailable when I need guidance. I feel unsupported in my role and unsure about what I need to do to advance.",
    "The workload distribution on our team is very uneven. A few of us carry most of the weight while others seem to have very light schedules. This is creating resentment.",
    "I am disappointed with the lack of growth opportunities. The training budget was cut this quarter and there is no clear promotion timeline despite my strong performance reviews.",
    "The micromanagement has increased significantly this quarter. Every small decision requires multiple approvals which slows down our work and kills creativity and initiative.",
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GENERATE EMPLOYEES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def generate_employees(n=500):
    """Generate n employee records with realistic correlations."""
    employees = []
    
    for i in range(1, n + 1):
        gender = random.choice(["Male", "Female"])
        if gender == "Male":
            first_name = random.choice(FIRST_NAMES_MALE)
        else:
            first_name = random.choice(FIRST_NAMES_FEMALE)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        
        department = random.choice(DEPARTMENTS)
        job_role = random.choice(JOB_ROLES[department])
        
        age = random.randint(22, 58)
        tenure_years = min(random.randint(0, 20), age - 21)
        years_at_company = min(random.randint(0, tenure_years + 1), tenure_years)
        
        # Salary based on department and tenure
        base_salaries = {
            "Engineering": 75000, "Sales": 60000, "Marketing": 55000,
            "HR": 55000, "Finance": 65000, "Operations": 58000,
        }
        base = base_salaries[department]
        salary = int(base + tenure_years * random.randint(2000, 5000) + random.randint(-5000, 15000))
        monthly_income = round(salary / 12, 2)
        salary_hike_percent = round(random.uniform(5, 25), 1)
        
        distance_from_home = random.randint(1, 45)
        num_companies_worked = random.randint(0, min(8, tenure_years))
        years_since_last_promotion = random.randint(0, min(6, years_at_company))
        absences_per_year = random.randint(0, 20)
        
        # Core satisfaction metrics (correlated)
        base_satisfaction = random.uniform(0, 1)
        job_satisfaction = max(1, min(4, round(base_satisfaction * 3 + random.uniform(0.5, 1.5))))
        work_life_balance = max(1, min(4, round(base_satisfaction * 3 + random.uniform(0.5, 1.5))))
        performance_rating = max(1, min(4, round(base_satisfaction * 2 + random.uniform(1, 2))))
        manager_rating = max(1, min(5, round(base_satisfaction * 3 + random.uniform(1, 2))))
        
        # Overtime — higher probability if low satisfaction
        overtime_prob = 0.35 if job_satisfaction >= 3 else 0.55
        overtime = "Yes" if random.random() < overtime_prob else "No"
        
        # ── Attrition logic (realistic correlations) ──
        # Target: ~16% attrition rate
        attrition_score = 0.0
        
        # Low satisfaction → higher attrition
        if job_satisfaction <= 2:
            attrition_score += 0.25
        if work_life_balance <= 2:
            attrition_score += 0.15
            
        # Overtime → higher attrition
        if overtime == "Yes":
            attrition_score += 0.12
            
        # Low salary hike → higher attrition
        if salary_hike_percent < 12:
            attrition_score += 0.08
            
        # Long time since promotion → higher attrition
        if years_since_last_promotion >= 4:
            attrition_score += 0.15
        elif years_since_last_promotion >= 2:
            attrition_score += 0.05
            
        # Low manager rating → higher attrition
        if manager_rating <= 2:
            attrition_score += 0.12
            
        # High distance from home → slight attrition increase
        if distance_from_home > 25:
            attrition_score += 0.06
            
        # Many companies worked → job hopper tendency
        if num_companies_worked >= 5:
            attrition_score += 0.08
            
        # Low tenure at company (new hires churn more)
        if years_at_company <= 1:
            attrition_score += 0.08
            
        # High absences → indicator
        if absences_per_year > 12:
            attrition_score += 0.06
            
        # Random noise
        attrition_score += random.uniform(-0.05, 0.10)
        
        # Threshold to get ~16% attrition rate
        attrition = "Yes" if attrition_score > 0.78 else "No"
        
        employees.append({
            "employee_id": f"EMP-{i:04d}",
            "name": name,
            "age": age,
            "gender": gender,
            "department": department,
            "job_role": job_role,
            "tenure_years": tenure_years,
            "salary": salary,
            "salary_hike_percent": salary_hike_percent,
            "monthly_income": monthly_income,
            "distance_from_home": distance_from_home,
            "job_satisfaction": job_satisfaction,
            "work_life_balance": work_life_balance,
            "overtime": overtime,
            "performance_rating": performance_rating,
            "num_companies_worked": num_companies_worked,
            "years_at_company": years_at_company,
            "years_since_last_promotion": years_since_last_promotion,
            "manager_rating": manager_rating,
            "absences_per_year": absences_per_year,
            "attrition": attrition,
        })
    
    return employees


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GENERATE FEEDBACK SURVEYS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def generate_feedback_surveys(employees, n=500):
    """Generate n feedback survey records linked to employees."""
    surveys = []
    quarters = ["Q1-2024", "Q2-2024", "Q3-2024", "Q4-2024", "Q1-2025"]
    
    for i in range(n):
        emp = random.choice(employees)
        quarter = random.choice(quarters)
        
        # Sentiment distribution: 60% positive, 25% neutral, 15% negative
        # But correlate with employee satisfaction
        if emp["job_satisfaction"] >= 3 and emp["work_life_balance"] >= 3:
            # Happy employees — skew more positive
            roll = random.random()
            if roll < 0.75:
                sentiment = "positive"
                feedback = random.choice(POSITIVE_FEEDBACK)
            elif roll < 0.92:
                sentiment = "neutral"
                feedback = random.choice(NEUTRAL_FEEDBACK)
            else:
                sentiment = "negative"
                feedback = random.choice(NEGATIVE_FEEDBACK)
        elif emp["job_satisfaction"] <= 2 or emp["work_life_balance"] <= 2:
            # Unhappy employees — skew more negative
            roll = random.random()
            if roll < 0.30:
                sentiment = "positive"
                feedback = random.choice(POSITIVE_FEEDBACK)
            elif roll < 0.55:
                sentiment = "neutral"
                feedback = random.choice(NEUTRAL_FEEDBACK)
            else:
                sentiment = "negative"
                feedback = random.choice(NEGATIVE_FEEDBACK)
        else:
            # Middle-of-the-road
            roll = random.random()
            if roll < 0.55:
                sentiment = "positive"
                feedback = random.choice(POSITIVE_FEEDBACK)
            elif roll < 0.82:
                sentiment = "neutral"
                feedback = random.choice(NEUTRAL_FEEDBACK)
            else:
                sentiment = "negative"
                feedback = random.choice(NEGATIVE_FEEDBACK)
        
        surveys.append({
            "employee_id": emp["employee_id"],
            "quarter": quarter,
            "feedback_text": feedback,
            "sentiment_label": sentiment,
        })
    
    return surveys


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GENERATE PERFORMANCE HISTORY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def generate_performance_history(employees, n_employees=50, n_quarters=8):
    """Generate quarterly performance data for n_employees over n_quarters."""
    history = []
    quarters = ["Q1-2023", "Q2-2023", "Q3-2023", "Q4-2023", "Q1-2024", "Q2-2024", "Q3-2024", "Q4-2024"]
    
    # Pick first n_employees that exist
    selected = employees[:n_employees]
    
    for emp in selected:
        # Base performance level for this employee (consistency)
        base_kpi = random.uniform(45, 85)
        trend = random.uniform(-1.5, 2.5)  # slight upward or downward trend
        
        for q_idx, quarter in enumerate(quarters[:n_quarters]):
            # KPI with trend + noise
            kpi_score = round(min(100, max(0, base_kpi + trend * q_idx + random.uniform(-10, 10))), 1)
            
            # Goals met correlated with KPI
            goals_met = round(min(100, max(0, kpi_score * random.uniform(0.85, 1.15) + random.uniform(-5, 5))), 1)
            
            # Projects completed — roughly proportional to KPI
            projects_completed = max(0, round(kpi_score / 20 + random.uniform(-1, 2)))
            
            # Team rating — somewhat correlated with KPI
            team_rating = round(min(5.0, max(1.0, kpi_score / 20 + random.uniform(-0.5, 0.5))), 1)
            
            history.append({
                "employee_id": emp["employee_id"],
                "quarter": quarter,
                "kpi_score": kpi_score,
                "goals_met": goals_met,
                "projects_completed": projects_completed,
                "team_rating": team_rating,
            })
    
    return history


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WRITE CSV FILES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def write_csv(filename, data, fieldnames):
    """Write a list of dicts to a CSV file."""
    filepath = DATA_DIR / filename
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"  ✓ Generated {filepath} ({len(data)} rows)")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    print("━" * 50)
    print("HRPulse — Generating Mock Data")
    print("━" * 50)
    print()
    
    # 1. Employees
    print("1. Generating employees.csv (500 rows)...")
    employees = generate_employees(500)
    write_csv("employees.csv", employees, [
        "employee_id", "name", "age", "gender", "department", "job_role",
        "tenure_years", "salary", "salary_hike_percent", "monthly_income",
        "distance_from_home", "job_satisfaction", "work_life_balance",
        "overtime", "performance_rating", "num_companies_worked",
        "years_at_company", "years_since_last_promotion", "manager_rating",
        "absences_per_year", "attrition",
    ])
    
    # Count attrition rate
    attrition_count = sum(1 for e in employees if e["attrition"] == "Yes")
    attrition_rate = attrition_count / len(employees) * 100
    print(f"     Attrition rate: {attrition_rate:.1f}% ({attrition_count}/{len(employees)})")
    print()
    
    # 2. Feedback Surveys
    print("2. Generating feedback_surveys.csv (500 rows)...")
    surveys = generate_feedback_surveys(employees, 500)
    write_csv("feedback_surveys.csv", surveys, [
        "employee_id", "quarter", "feedback_text", "sentiment_label",
    ])
    
    # Count sentiment distribution
    pos = sum(1 for s in surveys if s["sentiment_label"] == "positive")
    neu = sum(1 for s in surveys if s["sentiment_label"] == "neutral")
    neg = sum(1 for s in surveys if s["sentiment_label"] == "negative")
    print(f"     Sentiment distribution: positive={pos}, neutral={neu}, negative={neg}")
    print()
    
    # 3. Performance History
    print("3. Generating performance_history.csv (50 employees × 8 quarters)...")
    history = generate_performance_history(employees, 50, 8)
    write_csv("performance_history.csv", history, [
        "employee_id", "quarter", "kpi_score", "goals_met",
        "projects_completed", "team_rating",
    ])
    print()
    
    # 4. Verify static files exist
    print("4. Verifying static data files...")
    static_files = ["hr_policies.txt", "job_descriptions.json", "resumes.json"]
    for sf in static_files:
        path = DATA_DIR / sf
        if path.exists():
            size = path.stat().st_size
            print(f"  ✓ {sf} ({size:,} bytes)")
        else:
            print(f"  ✗ {sf} — MISSING! Please create this file.")
    
    print()
    print("━" * 50)
    print("Mock data generation complete!")
    print(f"All files saved to: {DATA_DIR.resolve()}")
    print("━" * 50)


if __name__ == "__main__":
    main()
