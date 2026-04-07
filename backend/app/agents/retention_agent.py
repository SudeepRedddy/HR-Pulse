"""
HRPulse — Retention Agent (LangGraph Workflow)
Autonomous workflow: analyze_risk → compose_email → notify_manager → schedule_meeting → done

Input: employee_id + risk_score + key risk factors (from SHAP)
Output: retention email, manager notification, suggested meeting slots
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, TypedDict

from app.core.config import settings

try:
    from langgraph.graph import END, StateGraph
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


# ── Agent State ──────────────────────────────
class RetentionState(TypedDict):
    employee_id: str
    employee_name: str
    department: str
    risk_score: float
    risk_factors: List[str]
    retention_email: str
    manager_notification: str
    meeting_slots: List[str]
    status: str
    steps: List[Dict[str, Any]]


# ── Node Functions ───────────────────────────
def analyze_risk(state: RetentionState) -> RetentionState:
    """Analyze the employee's risk profile and generate insights."""
    state["steps"].append({
        "agent": "Retention Agent",
        "action": "Analyzing risk factors",
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
    })

    # Enhance risk factors with actionable insights
    risk_insights = []
    for factor in state["risk_factors"]:
        factor_lower = factor.lower()
        if "satisfaction" in factor_lower:
            risk_insights.append("Low job satisfaction — consider role enrichment or project reassignment")
        elif "overtime" in factor_lower:
            risk_insights.append("Excessive overtime — review workload distribution and hire additional support")
        elif "promotion" in factor_lower:
            risk_insights.append("Overdue for promotion — initiate career progression discussion")
        elif "manager" in factor_lower:
            risk_insights.append("Low manager rating — consider management coaching or team transfer")
        elif "salary" in factor_lower or "hike" in factor_lower:
            risk_insights.append("Below-market compensation — prepare retention counter-offer")
        else:
            risk_insights.append(f"Risk factor identified: {factor}")

    state["risk_factors"] = risk_insights if risk_insights else state["risk_factors"]
    return state


def compose_email(state: RetentionState) -> RetentionState:
    """Compose a personalized retention email for the employee."""
    name = state["employee_name"]
    dept = state["department"]
    risk_score = state["risk_score"]
    factors = state["risk_factors"]

    # Try LLM first
    email = _generate_retention_email_mock(name, dept, risk_score, factors)

    try:
        from langchain_community.chat_models import ChatOllama
        llm = ChatOllama(model=settings.OLLAMA_MODEL, base_url=settings.OLLAMA_BASE_URL, temperature=0.7)
        prompt = f"""Write a warm, professional retention email to {name} in the {dept} department.
The employee has been identified as at-risk (score: {risk_score:.0%}).
Key concerns: {', '.join(factors[:3])}

The email should:
- Be empathetic and personal
- Acknowledge their value to the team
- Invite them to a one-on-one discussion
- Not directly mention their "risk score"
- Be 150-200 words

Write only the email body, starting with "Dear {name},"."""

        response = llm.invoke(prompt)
        email = response.content
    except Exception:
        pass

    state["retention_email"] = email
    state["steps"].append({
        "agent": "Retention Agent",
        "action": "Composing personalized retention email",
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
    })
    return state


def notify_manager(state: RetentionState) -> RetentionState:
    """Generate a manager notification about the at-risk employee."""
    name = state["employee_name"]
    dept = state["department"]
    risk_score = state["risk_score"]
    factors = state["risk_factors"]

    notification = f"""⚠ RETENTION ALERT — Confidential

Employee: {name}
Department: {dept}
Risk Level: {"HIGH" if risk_score >= 0.7 else "MEDIUM" if risk_score >= 0.4 else "LOW"} ({risk_score:.0%})

Key Risk Factors:
{chr(10).join(f"  • {f}" for f in factors[:4])}

Recommended Actions:
  1. Schedule a private one-on-one within the next 48 hours
  2. Review workload and recent project assignments
  3. Discuss career development goals and growth opportunities
  4. Consider compensation adjustment if applicable
  5. Document the conversation and agreed action items

Please treat this information confidentially. Contact HR for support.

— HRPulse Retention System"""

    state["manager_notification"] = notification
    state["steps"].append({
        "agent": "Retention Agent",
        "action": "Generating manager notification",
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
    })
    return state


def schedule_meeting(state: RetentionState) -> RetentionState:
    """Generate suggested meeting slots for the next 3 business days."""
    today = datetime.now()
    slots = []

    days_added = 0
    current = today + timedelta(days=1)
    while days_added < 3:
        if current.weekday() < 5:  # Monday-Friday
            date_str = current.strftime("%A, %B %d, %Y")
            slots.extend([
                f"{date_str} at 10:00 AM",
                f"{date_str} at 2:00 PM",
                f"{date_str} at 4:00 PM",
            ])
            days_added += 1
        current += timedelta(days=1)

    state["meeting_slots"] = slots
    state["status"] = "completed"
    state["steps"].append({
        "agent": "Retention Agent",
        "action": "Suggesting meeting slots",
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
    })
    return state


def _generate_retention_email_mock(name: str, dept: str, risk_score: float, factors: List[str]) -> str:
    """Generate a mock retention email."""
    factor_text = "\n".join(f"  - {f}" for f in factors[:3]) if factors else "  - General workplace satisfaction"

    return f"""Dear {name},

I hope this message finds you well. I wanted to reach out personally because you are a valued member of our {dept} team, and your contributions have not gone unnoticed.

I understand that certain aspects of your work experience may not be meeting your expectations, and I genuinely want to address that. Your talent and dedication are important to us, and I want to ensure we're providing an environment where you can thrive and grow.

I would love the opportunity to sit down with you for a confidential one-on-one conversation. I'd like to hear your thoughts on how we can better support your career goals and improve your day-to-day experience here at HRPulse.

Would you be available to meet this week? Please feel free to suggest a time that works best for you, or I can arrange a slot that fits your schedule.

Your voice matters to us, and I look forward to our conversation.

Warm regards,
HR Team
HRPulse Inc."""


# ── Build LangGraph Workflow ─────────────────
def _build_graph():
    """Build the retention agent LangGraph workflow."""
    if not LANGGRAPH_AVAILABLE:
        return None

    workflow = StateGraph(RetentionState)

    # Add nodes
    workflow.add_node("analyze_risk", analyze_risk)
    workflow.add_node("compose_email", compose_email)
    workflow.add_node("notify_manager", notify_manager)
    workflow.add_node("schedule_meeting", schedule_meeting)

    # Define edges (linear flow)
    workflow.set_entry_point("analyze_risk")
    workflow.add_edge("analyze_risk", "compose_email")
    workflow.add_edge("compose_email", "notify_manager")
    workflow.add_edge("notify_manager", "schedule_meeting")
    workflow.add_edge("schedule_meeting", END)

    return workflow.compile()


async def run_retention_workflow(
    employee_id: str,
    employee_name: str,
    department: str,
    risk_score: float,
    risk_factors: List[str],
) -> Dict:
    """
    Execute the full retention agent workflow.
    Returns complete results including email, notification, and meeting slots.
    """
    initial_state: RetentionState = {
        "employee_id": employee_id,
        "employee_name": employee_name,
        "department": department,
        "risk_score": risk_score,
        "risk_factors": risk_factors or ["General attrition risk"],
        "retention_email": "",
        "manager_notification": "",
        "meeting_slots": [],
        "status": "pending",
        "steps": [],
    }

    graph = _build_graph()

    if graph is not None:
        try:
            result = graph.invoke(initial_state)
            return result
        except Exception as e:
            print(f"  [RetentionAgent] LangGraph execution failed: {e}")

    # Fallback: run nodes sequentially
    state = initial_state
    state = analyze_risk(state)
    state = compose_email(state)
    state = notify_manager(state)
    state = schedule_meeting(state)
    return state
