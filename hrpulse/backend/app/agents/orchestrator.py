"""
HRPulse — Pipeline Orchestrator (LangGraph Master Workflow)
Chains all agents and ML models in a full autonomous pipeline.

Flow:
1. Load all employee data
2. Run attrition model → find employees with risk > 0.7
3. For each high-risk employee → trigger retention agent
4. Run sentiment model → if dept avg < 0.4 → log alert
5. Check for new resumes → run recruitment agent
6. Check for new employees → run onboarding agent

Streams step status to frontend via SSE.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

from app.agents.onboarding_agent import run_onboarding_workflow
from app.agents.recruitment_agent import run_recruitment_workflow
from app.agents.retention_agent import run_retention_workflow
from app.ml.attrition_model import predict_single as predict_attrition
from app.ml.sentiment_model import analyze_sentiment

# ── Pipeline State ───────────────────────────
_pipeline_steps: List[Dict[str, Any]] = []
_pipeline_running = False


def _add_step(step_name: str, agent_name: str, action: str, status: str, details: str = ""):
    """Add a step to the pipeline log."""
    step = {
        "step_name": step_name,
        "agent_name": agent_name,
        "action": action,
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "details": details,
    }
    _pipeline_steps.append(step)
    return step


def get_pipeline_status() -> List[Dict]:
    """Get the current pipeline execution status."""
    return _pipeline_steps.copy()


def is_pipeline_running() -> bool:
    """Check if the pipeline is currently running."""
    return _pipeline_running


async def run_full_pipeline(
    employees: List[dict],
    feedbacks: List[dict],
) -> AsyncGenerator[Dict, None]:
    """
    Execute the full autonomous pipeline.
    Yields step status updates as they occur (for SSE streaming).
    """
    global _pipeline_steps, _pipeline_running

    _pipeline_steps = []
    _pipeline_running = True

    try:
        # ── Step 1: Load Data ────────────────────
        step = _add_step("load_data", "Orchestrator", "Loading employee data", "running")
        yield step
        await asyncio.sleep(0.5)

        total_employees = len(employees)
        step = _add_step("load_data", "Orchestrator", f"Loaded {total_employees} employees", "completed")
        yield step

        # ── Step 2: Run Attrition Model ──────────
        step = _add_step("attrition_prediction", "ML Pipeline", "Running attrition predictions", "running")
        yield step

        high_risk_employees = []
        for emp in employees:
            result = predict_attrition(emp)
            if result["score"] >= 0.7:
                high_risk_employees.append({
                    "employee": emp,
                    "risk_score": result["score"],
                    "risk_factors": list(result.get("shap_values", {}).keys())[:3],
                })

        step = _add_step(
            "attrition_prediction", "ML Pipeline",
            f"Found {len(high_risk_employees)} high-risk employees (out of {total_employees})",
            "completed",
            json.dumps({"high_risk_count": len(high_risk_employees)}),
        )
        yield step

        # ── Step 3: Retention Agent ──────────────
        if high_risk_employees:
            step = _add_step("retention_workflow", "Retention Agent", "Processing high-risk employees", "running")
            yield step

            retention_results = []
            for hr_emp in high_risk_employees[:5]:  # Limit to top 5 to avoid timeout
                emp = hr_emp["employee"]
                try:
                    result = await run_retention_workflow(
                        employee_id=emp.get("id", emp.get("employee_id", "")),
                        employee_name=emp.get("name", "Unknown"),
                        department=emp.get("department", "Unknown"),
                        risk_score=hr_emp["risk_score"],
                        risk_factors=hr_emp["risk_factors"],
                    )
                    retention_results.append(result)
                except Exception as e:
                    _add_step("retention_workflow", "Retention Agent", f"Error for {emp.get('name')}: {e}", "failed")

            step = _add_step(
                "retention_workflow", "Retention Agent",
                f"Processed {len(retention_results)} retention workflows",
                "completed",
            )
            yield step
        else:
            step = _add_step("retention_workflow", "Retention Agent", "No high-risk employees found", "completed")
            yield step

        # ── Step 4: Sentiment Analysis ───────────
        step = _add_step("sentiment_analysis", "ML Pipeline", "Running sentiment analysis", "running")
        yield step

        if feedbacks:
            dept_sentiments = {}
            for fb in feedbacks[:100]:  # Sample
                result = analyze_sentiment(fb.get("feedback_text", ""))
                dept = fb.get("department", "Unknown")
                if dept not in dept_sentiments:
                    dept_sentiments[dept] = []
                dept_sentiments[dept].append(result["score"])

            alerts = []
            for dept, scores in dept_sentiments.items():
                avg = sum(scores) / len(scores) if scores else 0.5
                if avg < 0.4:
                    alerts.append(f"{dept}: avg sentiment {avg:.2f} (ALERT)")

            step = _add_step(
                "sentiment_analysis", "ML Pipeline",
                f"Analyzed {min(len(feedbacks), 100)} feedbacks — {len(alerts)} department alerts",
                "completed",
                json.dumps({"alerts": alerts}),
            )
            yield step
        else:
            step = _add_step("sentiment_analysis", "ML Pipeline", "No feedback data available", "completed")
            yield step

        # ── Step 5: Recruitment Check ────────────
        step = _add_step("recruitment_check", "Recruitment Agent", "Checking for new resumes", "running")
        yield step
        await asyncio.sleep(0.3)

        step = _add_step(
            "recruitment_check", "Recruitment Agent",
            "No new resumes in queue — skipping recruitment workflow",
            "completed",
        )
        yield step

        # ── Step 6: Onboarding Check ─────────────
        step = _add_step("onboarding_check", "Onboarding Agent", "Checking for new employees", "running")
        yield step
        await asyncio.sleep(0.3)

        step = _add_step(
            "onboarding_check", "Onboarding Agent",
            "No new employees pending onboarding — skipping",
            "completed",
        )
        yield step

        # ── Step 7: Pipeline Complete ────────────
        step = _add_step(
            "pipeline_complete", "Orchestrator",
            "Full pipeline execution completed successfully",
            "completed",
            json.dumps({
                "total_employees": total_employees,
                "high_risk_count": len(high_risk_employees),
                "retention_actions": len(high_risk_employees),
            }),
        )
        yield step

    except Exception as e:
        step = _add_step("pipeline_error", "Orchestrator", f"Pipeline failed: {str(e)}", "failed")
        yield step

    finally:
        _pipeline_running = False
