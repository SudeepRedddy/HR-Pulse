"""
HRPulse — Upload API Routes
POST /api/upload/csv
POST /api/upload/resume
POST /api/upload/policy-doc
"""

import csv
import io
import json
import os
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.employee import Employee, UploadLog

router = APIRouter(prefix="/upload", tags=["Uploads"])

ALLOWED_CSV_EXTENSIONS = {".csv"}
ALLOWED_PDF_EXTENSIONS = {".pdf"}
ALLOWED_DOC_EXTENSIONS = {".txt", ".pdf", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/csv")
async def upload_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Upload employee CSV data. Returns preview and processes records."""
    # Validate file type
    filename = file.filename or "unknown.csv"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_CSV_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    # Read file
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    # Parse CSV
    try:
        text = content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")

    if not rows:
        raise HTTPException(status_code=400, detail="CSV file is empty")

    # Preview first 5 rows
    preview = rows[:5]

    # Save file
    save_path = settings.UPLOADS_DIR / filename
    with open(save_path, "wb") as f:
        f.write(content)

    # Log upload
    upload_log = UploadLog(
        filename=filename,
        file_type="csv",
        file_size=len(content),
        status="completed",
        records_processed=len(rows),
        uploaded_by=current_user.get("user_id"),
    )
    db.add(upload_log)

    return {
        "filename": filename,
        "file_type": "csv",
        "file_size": len(content),
        "status": "completed",
        "records_processed": len(rows),
        "columns": list(rows[0].keys()) if rows else [],
        "preview": preview,
        "message": f"Successfully uploaded {len(rows)} records",
    }


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Upload a candidate resume (PDF or TXT)."""
    filename = file.filename or "unknown.pdf"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in {".pdf", ".txt"}:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are allowed")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    # Extract text
    resume_text = ""
    if ext == ".pdf":
        try:
            from PyPDF2 import PdfReader
            pdf_reader = PdfReader(io.BytesIO(content))
            for page in pdf_reader.pages:
                resume_text += page.extract_text() or ""
        except ImportError:
            resume_text = "[PDF parsing unavailable — PyPDF2 not installed]"
        except Exception as e:
            resume_text = f"[PDF parsing failed: {str(e)}]"
    else:
        resume_text = content.decode("utf-8", errors="replace")

    # Save file
    save_path = settings.UPLOADS_DIR / filename
    with open(save_path, "wb") as f:
        f.write(content)

    # Log upload
    upload_log = UploadLog(
        filename=filename,
        file_type="resume",
        file_size=len(content),
        status="completed",
        records_processed=1,
        uploaded_by=current_user.get("user_id"),
    )
    db.add(upload_log)

    return {
        "filename": filename,
        "file_type": "resume",
        "file_size": len(content),
        "status": "completed",
        "records_processed": 1,
        "resume_text": resume_text[:2000],  # Truncate for response
        "message": f"Resume uploaded successfully ({len(resume_text)} characters extracted)",
    }


@router.post("/policy-doc")
async def upload_policy_doc(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Upload an HR policy document for RAG indexing."""
    filename = file.filename or "unknown.txt"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_DOC_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only TXT, PDF, DOC, and DOCX files are allowed")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    # Save to data directory for RAG pipeline
    save_path = settings.DATA_DIR / "hr_policies.txt"

    if ext == ".txt":
        text = content.decode("utf-8", errors="replace")
    elif ext == ".pdf":
        try:
            from PyPDF2 import PdfReader
            pdf_reader = PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
        except Exception:
            text = content.decode("utf-8", errors="replace")
    else:
        text = content.decode("utf-8", errors="replace")

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(text)

    # Also save original file
    original_path = settings.UPLOADS_DIR / filename
    with open(original_path, "wb") as fb:
        fb.write(content)

    # Log upload
    upload_log = UploadLog(
        filename=filename,
        file_type="policy",
        file_size=len(content),
        status="completed",
        records_processed=1,
        uploaded_by=current_user.get("user_id"),
    )
    db.add(upload_log)

    return {
        "filename": filename,
        "file_type": "policy",
        "file_size": len(content),
        "status": "completed",
        "records_processed": 1,
        "text_length": len(text),
        "message": "Policy document uploaded and indexed for RAG pipeline",
    }
