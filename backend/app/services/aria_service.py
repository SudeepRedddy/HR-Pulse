import asyncio
import json
import random
import httpx
from typing import List, Dict, Any
from app.core.config import settings


# ── Contextual response templates ──────────────
POLICY_RESPONSES = [
    "According to HRPulse policy records, full-time employees are entitled to 12 paid sick days per year, 20 vacation days, and 5 personal days. Sick leave can be carried over up to 5 days into the next fiscal year.",
    "Our parental leave policy provides 16 weeks of paid leave for primary caregivers and 4 weeks for secondary caregivers. This applies to all employees who have completed 6+ months of service.",
    "The remote work policy allows up to 3 days per week of remote work for eligible roles. Department heads can override this based on project requirements. All remote days must be logged in the attendance portal.",
]

RECRUITMENT_RESPONSES = [
    "I've reviewed recent candidate submissions. The Recruitment Portal shows {n} active job roles. To evaluate a new resume, navigate to the Recruitment tab, select a role, and upload the candidate's file. Our AI will generate a hire/no-hire recommendation instantly.",
    "Best practice for screening: upload the resume against the specific job role so the AI can match skills against requirements. The system checks for keyword alignment, experience patterns, and generates a plain-English hiring recommendation.",
    "Current recruitment pipeline is healthy. I recommend prioritizing roles that have been open for 30+ days. You can check time-to-fill metrics in the Executive Dashboard.",
]

ANALYTICS_RESPONSES = [
    "Here's a quick snapshot: Engineering typically holds the highest headcount at ~30% of the organization, followed by Sales at ~20%. The Executive Dashboard provides real-time breakdowns across all 6 departments including salary bracket distributions.",
    "Attrition analysis shows that employees with low job satisfaction (≤2/4) and regular overtime are 3x more likely to leave. The Performance Predictor on each employee card now provides individual risk assessments.",
    "Salary distribution data shows the majority of the workforce falls in the $50k–$80k bracket. The top 15% (typically Senior/Lead roles in Engineering and Finance) exceed $120k. All this is visualized in the PowerBI-style dashboard.",
]

PERFORMANCE_RESPONSES = [
    "The ML Performance Predictor uses a weighted scoring model across 6 key dimensions: performance rating (30%), job satisfaction (20%), work-life balance (15%), manager alignment (15%), tenure (10%), and attendance (10%). Each employee gets a score out of 100 and is classified as Top Performer, Steady Contributor, or Needs Attention.",
    "To view an employee's performance prediction, go to the Employee Directory, click on any employee row, and their dossier will open with the AI-generated assessment. The system provides specific, actionable recommendations for each tier.",
    "Our prediction model identifies three risk factors that most strongly correlate with attrition: stalled promotions (4+ years), overtime combined with low satisfaction, and manager misalignment. The system flags these automatically.",
]

GENERAL_RESPONSES = [
    "I'm ARIA, your AI-powered HR intelligence assistant. I can help with:\n\n• **Policy queries** — leave, benefits, remote work\n• **Recruitment screening** — resume analysis and hire recommendations\n• **Performance insights** — employee predictions and risk flags\n• **Analytics** — headcount, salary, and department data\n\nWhat would you like to explore?",
    "Welcome to HRPulse Intelligence. I can pull real-time analytics from your workforce data, help evaluate candidates, or answer questions about company policies. Just ask naturally — I understand context.",
]


async def get_aria_response(message: str, history: List[Any] = []) -> str:
    """
    Classify intent and return a contextual response.
    Attempts to query the configured Ollama LLM, falling back to mock logic if unavailable.
    """
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            payload = {
                "model": settings.OLLAMA_MODEL,
                "prompt": f"You are ARIA, an AI HR Assistant. Provide a brief, helpful, and professional HR-related response without mentioning you are an AI model unless asked. Please keep it strictly under 4 sentences.\nUser: {message}\nARIA:",
                "stream": False
            }
            res = await client.post(f"{settings.OLLAMA_BASE_URL}/api/generate", json=payload)
            if res.status_code == 200:
                data = res.json().get("response", "").strip()
                if data:
                    return data
    except Exception:
        pass  # Silently fallback to mock responses if LLM container is off or times out

    msg_lower = message.lower().strip()

    if any(kw in msg_lower for kw in ["leave", "policy", "sick", "remote", "vacation", "parental", "benefit"]):
        return random.choice(POLICY_RESPONSES)

    elif any(kw in msg_lower for kw in ["hire", "candidate", "resume", "recruit", "screening", "job", "applicant"]):
        return random.choice(RECRUITMENT_RESPONSES).format(n=random.randint(4, 8))

    elif any(kw in msg_lower for kw in ["headcount", "department", "salary", "analytics", "dashboard", "distribution", "attrition rate"]):
        return random.choice(ANALYTICS_RESPONSES)

    elif any(kw in msg_lower for kw in ["performance", "predictor", "predict", "employee", "risk", "burnout", "promotion"]):
        return random.choice(PERFORMANCE_RESPONSES)

    else:
        return random.choice(GENERAL_RESPONSES)


# ── Legacy SSE streaming generator (kept for compatibility) ──
async def generate_aria_response(message: str, history: List[Any]):
    """SSE stream version — used if frontend switches to EventSource."""
    response = await get_aria_response(message, history)

    for word in response.split(" "):
        yield f"event: token\ndata: {word} \n\n"
        await asyncio.sleep(0.04)

    yield f"event: done\ndata: {json.dumps({'status': 'complete'})}\n\n"
