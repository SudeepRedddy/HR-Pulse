"""
HRPulse — Recruitment API Routes
Handles Job Postings, Candidate Tracking, and automated AI Resume evaluation.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.employee import JobDescription, Candidate
from app.schemas.schemas import JobDescriptionBase, JobDescriptionResponse, CandidateResponse

router = APIRouter(prefix="/recruitment", tags=["Recruitment"])


@router.get("/jobs", response_model=List[JobDescriptionResponse])
async def list_jobs(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """List all available job descriptions."""
    result = await db.execute(select(JobDescription))
    jobs = result.scalars().all()
    return [JobDescriptionResponse.model_validate(job) for job in jobs]


@router.post("/jobs", response_model=JobDescriptionResponse)
async def create_job(
    request: JobDescriptionBase,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new job posting with interview questions."""
    new_job = JobDescription(
        title=request.title,
        department=request.department,
        required_skills=request.required_skills,
        nice_to_have_skills=request.nice_to_have_skills,
        interview_questions=request.interview_questions,
        description=request.description
    )
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    return JobDescriptionResponse.model_validate(new_job)

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Delete a job."""
    result = await db.execute(select(JobDescription).where(JobDescription.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    await db.delete(job)
    await db.commit()
    return {"status": "ok"}


@router.get("/candidates", response_model=List[CandidateResponse])
async def list_candidates(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """List all candidate applications."""
    result = await db.execute(select(Candidate))
    candidates = result.scalars().all()
    return [CandidateResponse.model_validate(c) for c in candidates]


@router.post("/candidates/upload", response_model=CandidateResponse)
async def upload_resume(
    name: str = Form(...),
    job_id: str = Form(...),
    resume: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a resume file, extract text, and automatically evaluate 'Should we hire?'.
    """
    # Fetch job description for comparison
    job_result = await db.execute(select(JobDescription).where(JobDescription.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    content = await resume.read()
    
    # Proper PDF Text Extraction
    resume_text = ""
    filename = resume.filename.lower() if resume.filename else ""
    if filename.endswith(".pdf"):
        import io
        try:
            from PyPDF2 import PdfReader
            pdf_reader = PdfReader(io.BytesIO(content))
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    resume_text += extracted + "\n"
        except ImportError:
            resume_text = "[PDF parsing unavailable — PyPDF2 not installed]"
        except Exception as e:
            resume_text = f"[PDF parsing failed: {str(e)}]"
    else:
        resume_text = content.decode('utf-8', errors='ignore')

    # Remove NUL bytes to prevent Postgres asyncpg CharacterNotInRepertoireError
    resume_text = resume_text.replace('\x00', '')

    # Simulated AI Parser / NLP matching logic
    # In a real scenario, this is where we send the resume_text and job.required_skills
    # to Gemini / OpenAI to return an english assessment string.
    ai_eval = ""
    # We do a naive fallback mock logic based on skills
    required_keywords = []
    if job.required_skills:
        try:
            required_keywords = json.loads(job.required_skills)
        except:
            required_keywords = job.required_skills.split(',')
    
    matches = sum([1 for kw in required_keywords if kw.strip().lower() in resume_text.lower()])
    
    if len(required_keywords) > 0 and matches >= len(required_keywords) / 2:
        ai_eval = f"Can we take him? Yes. This candidate matches several key skills for {job.title}. Recommend asking them Question #1 from your interview list to gauge their practical experience."
    elif len(required_keywords) > 0:
        ai_eval = f"Can we take him? Proceed with caution. The resume lacks mentions of core {job.title} skills. Schedule a brief screening call to verify technical baseline before a full interview."
    else:
        ai_eval = "Can we take him? Yes, looks like a standard fit for the role. Schedule an initial interview."

    new_candidate = Candidate(
        name=name,
        job_id=job_id,
        skills=json.dumps(required_keywords),  # Mocking extracted skills
        resume_text=resume_text,
        ai_evaluation=ai_eval,
        experience_years=match_experience(resume_text),
    )
    
    db.add(new_candidate)
    await db.commit()
    await db.refresh(new_candidate)

    return CandidateResponse.model_validate(new_candidate)

def match_experience(text: str) -> int:
    """Mock helper to guess experience years from text."""
    if "years" in text.lower():
        return 3
    return 1
