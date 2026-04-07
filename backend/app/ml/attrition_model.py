"""
HRPulse — Attrition Risk Prediction Model
XGBoost binary classifier with SHAP explainability.

Features: tenure, salary_hike, job_satisfaction, work_life_balance,
          overtime, performance_rating, distance_from_home, absences,
          years_since_last_promotion, manager_rating
Target: attrition (binary: 0/1)
Output: probability score 0.0–1.0 per employee
"""

import json
import os
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.preprocessing import LabelEncoder

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

from app.core.config import settings

# ── Paths ────────────────────────────────────
MODEL_PATH = settings.ML_MODELS_DIR / "attrition.pkl"
SHAP_EXPLAINER_PATH = settings.ML_MODELS_DIR / "attrition_shap.pkl"
DATA_PATH = settings.DATA_DIR / "employees.csv"

# ── Feature columns ─────────────────────────
FEATURE_COLUMNS = [
    "tenure_years",
    "salary_hike_percent",
    "job_satisfaction",
    "work_life_balance",
    "overtime_encoded",
    "performance_rating",
    "distance_from_home",
    "absences_per_year",
    "years_since_last_promotion",
    "manager_rating",
]

FEATURE_NAMES = [
    "Tenure (years)",
    "Salary Hike (%)",
    "Job Satisfaction",
    "Work-Life Balance",
    "Overtime",
    "Performance Rating",
    "Distance from Home",
    "Absences/Year",
    "Years Since Promotion",
    "Manager Rating",
]


def load_and_prepare_data() -> Tuple[pd.DataFrame, pd.Series]:
    """Load employees.csv and prepare features + target."""
    df = pd.read_csv(DATA_PATH)

    # Encode overtime: Yes=1, No=0
    df["overtime_encoded"] = (df["overtime"].str.strip().str.lower() == "yes").astype(int)

    # Encode target: Yes=1, No=0
    y = (df["attrition"].str.strip().str.lower() == "yes").astype(int)

    X = df[FEATURE_COLUMNS].copy()

    return X, y


def train_model() -> dict:
    """Train the XGBoost attrition model and save to disk."""
    print("  [Attrition] Loading data...")
    X, y = load_and_prepare_data()

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"  [Attrition] Training set: {len(X_train)} | Test set: {len(X_test)}")
    print(f"  [Attrition] Attrition rate: {y.mean()*100:.1f}%")

    if not XGBOOST_AVAILABLE:
        print("  [Attrition] XGBoost not available — saving mock model")
        mock_model = {"type": "mock", "features": FEATURE_COLUMNS}
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(mock_model, f)
        return {"status": "mock", "message": "XGBoost not installed"}

    # Train XGBoost
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=len(y_train[y_train == 0]) / max(len(y_train[y_train == 1]), 1),
        random_state=42,
        eval_metric="logloss",
        use_label_encoder=False,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    # Evaluate
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print(f"  [Attrition] Accuracy: {accuracy:.4f}")
    print(f"  [Attrition] AUC-ROC: {auc:.4f}")

    # Save model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"  [Attrition] Model saved to {MODEL_PATH}")

    # Save SHAP explainer
    if SHAP_AVAILABLE:
        print("  [Attrition] Computing SHAP explainer...")
        explainer = shap.TreeExplainer(model)
        with open(SHAP_EXPLAINER_PATH, "wb") as f:
            pickle.dump(explainer, f)
        print(f"  [Attrition] SHAP explainer saved to {SHAP_EXPLAINER_PATH}")

    report = classification_report(y_test, y_pred, output_dict=True)

    return {
        "status": "trained",
        "accuracy": accuracy,
        "auc_roc": auc,
        "report": report,
    }


def load_model():
    """Load the trained model from disk."""
    if not MODEL_PATH.exists():
        return None
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


def load_shap_explainer():
    """Load the SHAP explainer from disk."""
    if not SHAP_EXPLAINER_PATH.exists():
        return None
    with open(SHAP_EXPLAINER_PATH, "rb") as f:
        return pickle.load(f)


def predict_single(employee_data: dict) -> Dict:
    """
    Predict attrition risk for a single employee.
    Returns: {score: float, risk_level: str, shap_values: dict}
    """
    model = load_model()
    if model is None:
        return {"score": 0.5, "risk_level": "unknown", "shap_values": {}}

    # Handle mock model
    if isinstance(model, dict) and model.get("type") == "mock":
        # Generate a plausible mock score based on features
        satisfaction = employee_data.get("job_satisfaction", 3)
        overtime = 1 if str(employee_data.get("overtime", "No")).lower() == "yes" else 0
        mock_score = max(0, min(1, 0.3 + (4 - satisfaction) * 0.15 + overtime * 0.15))
        return {
            "score": round(mock_score, 4),
            "risk_level": _risk_level(mock_score),
            "shap_values": {name: round(np.random.uniform(-0.1, 0.1), 4) for name in FEATURE_NAMES},
        }

    # Prepare features
    overtime_encoded = 1 if str(employee_data.get("overtime", "No")).lower() == "yes" else 0
    features = np.array([[
        employee_data.get("tenure_years", 0),
        employee_data.get("salary_hike_percent", 15),
        employee_data.get("job_satisfaction", 3),
        employee_data.get("work_life_balance", 3),
        overtime_encoded,
        employee_data.get("performance_rating", 3),
        employee_data.get("distance_from_home", 10),
        employee_data.get("absences_per_year", 5),
        employee_data.get("years_since_last_promotion", 1),
        employee_data.get("manager_rating", 3),
    ]])

    # Predict probability
    proba = model.predict_proba(features)[0][1]
    score = round(float(proba), 4)

    # SHAP values
    shap_values_dict = {}
    explainer = load_shap_explainer()
    if explainer is not None:
        try:
            sv = explainer.shap_values(features)
            if isinstance(sv, list):
                sv = sv[1]  # For binary classification, use class 1
            for i, name in enumerate(FEATURE_NAMES):
                shap_values_dict[name] = round(float(sv[0][i]), 4)
        except Exception:
            for name in FEATURE_NAMES:
                shap_values_dict[name] = 0.0
    else:
        for name in FEATURE_NAMES:
            shap_values_dict[name] = 0.0

    return {
        "score": score,
        "risk_level": _risk_level(score),
        "shap_values": shap_values_dict,
    }


def predict_batch(employees: List[dict]) -> List[Dict]:
    """Predict attrition risk for a batch of employees."""
    return [predict_single(emp) for emp in employees]


def _risk_level(score: float) -> str:
    """Convert probability score to risk level label."""
    if score >= 0.7:
        return "high"
    elif score >= 0.4:
        return "medium"
    else:
        return "low"
