"""
HRPulse — Database Seed Script
Reads generated CSV/JSON data files and populates PostgreSQL on first run.
Runs automatically via docker-compose startup command.

Usage: python seed_data.py
"""

import csv
import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.database import Base, SyncSessionLocal, sync_engine
from app.core.security import hash_password
from app.models.employee import (
    Candidate,
    Employee,
    JobDescription,
    User,
)

DATA_DIR = settings.DATA_DIR


def check_if_seeded(session) -> bool:
    """Check if the database already has data."""
    count = session.query(Employee).count()
    return count > 0


def seed_users(session):
    """Seed the admin user."""
    print("  → Seeding users...")
    admin = User(
        id="USR-0001",
        email="admin@hrpulse.com",
        name="Admin User",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active=True,
    )
    session.add(admin)
    session.flush()
    print(f"    ✓ Created admin user: admin@hrpulse.com / admin123")


def seed_employees(session):
    """Seed employees from employees.csv."""
    print("  → Seeding employees...")
    csv_path = DATA_DIR / "employees.csv"

    if not csv_path.exists():
        print(f"    ✗ File not found: {csv_path}")
        print("    → Running data generator...")
        from generate_mock_data import main as generate_data
        generate_data()

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            emp = Employee(
                id=row["employee_id"],
                name=row["name"],
                age=int(row["age"]),
                gender=row["gender"],
                department=row["department"],
                job_role=row["job_role"],
                tenure_years=int(row["tenure_years"]),
                salary=int(row["salary"]),
                salary_hike_percent=float(row["salary_hike_percent"]),
                monthly_income=float(row["monthly_income"]),
                distance_from_home=int(row["distance_from_home"]),
                job_satisfaction=int(row["job_satisfaction"]),
                work_life_balance=int(row["work_life_balance"]),
                overtime=row["overtime"],
                performance_rating=int(row["performance_rating"]),
                num_companies_worked=int(row["num_companies_worked"]),
                years_at_company=int(row["years_at_company"]),
                years_since_last_promotion=int(row["years_since_last_promotion"]),
                manager_rating=int(row["manager_rating"]),
                absences_per_year=int(row["absences_per_year"]),
                attrition=row["attrition"],
            )
            session.add(emp)
            count += 1
        session.flush()
        print(f"    ✓ Seeded {count} employees")


def seed_job_descriptions(session):
    """Seed job descriptions from job_descriptions.json."""
    print("  → Seeding job descriptions...")
    json_path = DATA_DIR / "job_descriptions.json"

    if not json_path.exists():
        print(f"    ✗ File not found: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        jds = json.load(f)

    for jd in jds:
        job = JobDescription(
            id=jd["job_id"],
            title=jd["title"],
            department=jd["department"],
            required_skills=json.dumps(jd["required_skills"]),
            description=jd["description"],
            interview_questions=json.dumps([
                "What is your largest project experience?",
                "How do you handle conflict in a team?"
            ])
        )
        session.add(job)
    session.flush()
    print(f"    ✓ Seeded {len(jds)} job descriptions")


def seed_candidates(session):
    """Seed candidates from resumes.json."""
    print("  → Seeding candidates...")
    json_path = DATA_DIR / "resumes.json"

    if not json_path.exists():
        print(f"    ✗ File not found: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    for c in candidates:
        candidate = Candidate(
            id=c["candidate_id"],
            name=c["name"],
            experience_years=c["experience_years"],
            ai_evaluation="Strong candidate with relevant skills in " + ", ".join(c.get("skills", [])),
            job_id=None # Will be linked manually in demo
        )
        session.add(candidate)
    session.flush()
    print(f"    ✓ Seeded {len(candidates)} candidates")


def main():
    """Main seed function — creates tables and populates data."""
    print()
    print("━" * 50)
    print("  HRPulse — Database Seeding")
    print("━" * 50)
    print()

    # Create all tables
    print("  → Creating database tables...")
    Base.metadata.create_all(bind=sync_engine)
    print("    ✓ Tables created")
    print()

    session = SyncSessionLocal()

    try:
        # Check if already seeded
        if check_if_seeded(session):
            print("  ℹ Database already seeded. Skipping.")
            print()
            print("━" * 50)
            print("  Seeding complete (no changes)")
            print("━" * 50)
            return

        # Seed all data
        seed_users(session)
        seed_employees(session)
        seed_job_descriptions(session)
        seed_candidates(session)

        # Commit all changes
        session.commit()

        print()
        print("━" * 50)
        print("  ✓ Database seeding complete!")
        print("    • 1 admin user")
        print("    • 500 employees")
        print("    • 6 job descriptions")
        print("    • 20 candidates")
        print("━" * 50)

    except Exception as e:
        session.rollback()
        print(f"\n  ✗ Seeding failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
