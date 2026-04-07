"""
HRPulse — ML Service
Orchestrates all ML model training and inference.
"""

import json
from typing import Dict, List, Optional

from app.ml import attrition_model, performance_model, sentiment_model, skill_gap_model


def train_all_models() -> Dict[str, dict]:
    """Train all ML models and return training results."""
    print()
    print("━" * 50)
    print("  HRPulse — Training All ML Models")
    print("━" * 50)
    print()

    results = {}

    # 1. Attrition Model
    print("─── Model 1: Attrition (XGBoost) ───")
    try:
        results["attrition"] = attrition_model.train_model()
    except Exception as e:
        print(f"  ✗ Attrition training failed: {e}")
        results["attrition"] = {"status": "error", "message": str(e)}
    print()

    # 2. Skill Gap Model (before sentiment, as it's lighter)
    print("─── Model 3: Skill Gap (TF-IDF + KMeans) ───")
    try:
        results["skill_gap"] = skill_gap_model.train_model()
    except Exception as e:
        print(f"  ✗ Skill gap training failed: {e}")
        results["skill_gap"] = {"status": "error", "message": str(e)}
    print()

    # 3. Performance Forecast Model
    print("─── Model 4: Performance (LSTM) ───")
    try:
        results["performance"] = performance_model.train_model()
    except Exception as e:
        print(f"  ✗ Performance training failed: {e}")
        results["performance"] = {"status": "error", "message": str(e)}
    print()

    # 4. Sentiment Model (no training needed, pretrained)
    print("─── Model 2: Sentiment (DistilBERT) ───")
    print("  [Sentiment] Using pretrained model — no training required")
    print("  [Sentiment] Model will be lazy-loaded on first inference")
    results["sentiment"] = {"status": "pretrained", "model": "distilbert-base-uncased-finetuned-sst-2-english"}
    print()

    print("━" * 50)
    print("  ML Model Training Complete!")
    for name, result in results.items():
        status = result.get("status", "unknown")
        icon = "✓" if status in ("trained", "pretrained") else "⚠" if status == "mock" else "✗"
        print(f"    {icon} {name}: {status}")
    print("━" * 50)

    return results


def get_employee_predictions(employee_data: dict) -> Dict:
    """Get all ML predictions for a single employee."""
    results = {}

    # Attrition risk
    try:
        results["attrition"] = attrition_model.predict_single(employee_data)
    except Exception as e:
        results["attrition"] = {"score": 0.5, "risk_level": "unknown", "error": str(e)}

    return results


def get_sentiment_analysis(text: str) -> Dict:
    """Run sentiment analysis on a single text."""
    return sentiment_model.analyze_sentiment(text)


def get_sentiment_batch(texts: List[str]) -> List[Dict]:
    """Run sentiment analysis on a batch of texts."""
    return sentiment_model.analyze_batch(texts)


def get_skill_gap_analysis(candidate_skills: List[str], job_id: str) -> Dict:
    """Analyze skill gap for a candidate against a job."""
    return skill_gap_model.analyze_candidate_for_job(
        candidate_id="",  # Will be looked up by skills
        job_id=job_id,
    )


def get_performance_forecast(kpi_history: List[float]) -> Dict:
    """Forecast next quarter KPI for an employee."""
    return performance_model.predict_next_quarter(kpi_history)
