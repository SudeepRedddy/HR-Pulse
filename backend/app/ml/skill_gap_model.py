"""
HRPulse — Skill Gap Analysis Model
TF-IDF vectorization + KMeans clustering + cosine similarity.

Compares employee/candidate skills against job description required skills.
Output: match score 0-100, list of matched skills, list of missing skills.
"""

import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from app.core.config import settings

# ── Paths ────────────────────────────────────
VECTORIZER_PATH = settings.ML_MODELS_DIR / "skill_vectorizer.pkl"
CLUSTER_MODEL_PATH = settings.ML_MODELS_DIR / "skill_clusters.pkl"
JD_PATH = settings.DATA_DIR / "job_descriptions.json"
RESUMES_PATH = settings.DATA_DIR / "resumes.json"


def load_job_descriptions() -> List[dict]:
    """Load job descriptions from JSON file."""
    if not JD_PATH.exists():
        return []
    with open(JD_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_resumes() -> List[dict]:
    """Load candidate resumes from JSON file."""
    if not RESUMES_PATH.exists():
        return []
    with open(RESUMES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def train_model() -> dict:
    """Train the TF-IDF vectorizer and KMeans clustering model."""
    print("  [SkillGap] Loading data...")

    jds = load_job_descriptions()
    resumes = load_resumes()

    if not jds or not resumes:
        print("  [SkillGap] No data available — saving mock model")
        return {"status": "mock", "message": "No data files found"}

    if not SKLEARN_AVAILABLE:
        print("  [SkillGap] scikit-learn not available — saving mock model")
        return {"status": "mock", "message": "scikit-learn not installed"}

    # Build skill corpus: combine all skills from JDs and resumes
    all_skill_texts = []

    for jd in jds:
        skills = jd.get("required_skills", []) + jd.get("nice_to_have_skills", [])
        skill_text = " ".join(skills).lower()
        all_skill_texts.append(skill_text)

    for resume in resumes:
        skills = resume.get("skills", [])
        skill_text = " ".join(skills).lower()
        all_skill_texts.append(skill_text)

    # Train TF-IDF vectorizer
    print(f"  [SkillGap] Training TF-IDF on {len(all_skill_texts)} documents...")
    vectorizer = TfidfVectorizer(
        max_features=200,
        stop_words="english",
        ngram_range=(1, 2),
    )
    tfidf_matrix = vectorizer.fit_transform(all_skill_texts)

    # Train KMeans clustering
    n_clusters = min(6, len(all_skill_texts))
    print(f"  [SkillGap] Training KMeans with {n_clusters} clusters...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(tfidf_matrix)

    # Save models
    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)
    print(f"  [SkillGap] Vectorizer saved to {VECTORIZER_PATH}")

    with open(CLUSTER_MODEL_PATH, "wb") as f:
        pickle.dump(kmeans, f)
    print(f"  [SkillGap] Cluster model saved to {CLUSTER_MODEL_PATH}")

    return {
        "status": "trained",
        "n_documents": len(all_skill_texts),
        "n_features": len(vectorizer.get_feature_names_out()),
        "n_clusters": n_clusters,
    }


def load_vectorizer():
    """Load the trained TF-IDF vectorizer."""
    if not VECTORIZER_PATH.exists():
        return None
    with open(VECTORIZER_PATH, "rb") as f:
        return pickle.load(f)


def analyze_skill_gap(
    candidate_skills: List[str],
    job_required_skills: List[str],
    job_nice_to_have: Optional[List[str]] = None,
) -> Dict:
    """
    Analyze skill gap between a candidate and a job description.
    Returns: {match_score: int, matched_skills: list, missing_skills: list,
              nice_to_have_matched: list, similarity_score: float}
    """
    if not candidate_skills or not job_required_skills:
        return {
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": job_required_skills or [],
            "nice_to_have_matched": [],
            "similarity_score": 0.0,
        }

    # Normalize skills for comparison
    candidate_lower = {s.lower().strip() for s in candidate_skills}
    required_lower = {s.lower().strip() for s in job_required_skills}

    # Direct skill matching
    matched = candidate_lower & required_lower
    missing = required_lower - candidate_lower

    # Map back to original casing
    matched_skills = [s for s in job_required_skills if s.lower().strip() in matched]
    missing_skills = [s for s in job_required_skills if s.lower().strip() in missing]

    # Nice-to-have matching
    nice_matched = []
    if job_nice_to_have:
        nice_lower = {s.lower().strip() for s in job_nice_to_have}
        nice_match = candidate_lower & nice_lower
        nice_matched = [s for s in job_nice_to_have if s.lower().strip() in nice_match]

    # Calculate match score (0-100)
    required_score = (len(matched_skills) / max(len(job_required_skills), 1)) * 80
    nice_score = (len(nice_matched) / max(len(job_nice_to_have or []), 1)) * 20
    match_score = round(required_score + nice_score)

    # TF-IDF cosine similarity (if vectorizer is available)
    similarity_score = 0.0
    vectorizer = load_vectorizer()
    if vectorizer is not None and SKLEARN_AVAILABLE:
        try:
            candidate_text = " ".join(candidate_skills).lower()
            job_text = " ".join(job_required_skills + (job_nice_to_have or [])).lower()
            vectors = vectorizer.transform([candidate_text, job_text])
            sim = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            similarity_score = round(float(sim), 4)
        except Exception:
            pass

    return {
        "match_score": match_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "nice_to_have_matched": nice_matched,
        "similarity_score": similarity_score,
    }


def analyze_candidate_for_job(candidate_id: str, job_id: str) -> Dict:
    """Analyze a specific candidate against a specific job description."""
    jds = load_job_descriptions()
    resumes = load_resumes()

    job = next((j for j in jds if j["job_id"] == job_id), None)
    candidate = next((r for r in resumes if r["candidate_id"] == candidate_id), None)

    if not job or not candidate:
        return {"error": "Job or candidate not found"}

    result = analyze_skill_gap(
        candidate_skills=candidate["skills"],
        job_required_skills=job["required_skills"],
        job_nice_to_have=job.get("nice_to_have_skills"),
    )

    result["candidate_name"] = candidate["name"]
    result["job_title"] = job["title"]
    result["department"] = job["department"]
    result["experience_years"] = candidate["experience_years"]

    return result


def rank_candidates_for_job(job_id: str) -> List[Dict]:
    """Rank all candidates for a specific job description."""
    jds = load_job_descriptions()
    resumes = load_resumes()

    job = next((j for j in jds if j["job_id"] == job_id), None)
    if not job:
        return []

    rankings = []
    for candidate in resumes:
        result = analyze_skill_gap(
            candidate_skills=candidate["skills"],
            job_required_skills=job["required_skills"],
            job_nice_to_have=job.get("nice_to_have_skills"),
        )
        result["candidate_id"] = candidate["candidate_id"]
        result["candidate_name"] = candidate["name"]
        result["experience_years"] = candidate["experience_years"]
        rankings.append(result)

    # Sort by match score descending
    rankings.sort(key=lambda x: x["match_score"], reverse=True)

    return rankings
