"""
HRPulse — Recruitment Agent (LangGraph Workflow)
Pipeline: parse_resume → score_fit → rank_candidates → draft_interview_email

Input: resume text (from PDF) + job description
Output: fit score, matched/missing skills, interview email draft
"""

from datetime import datetime
from typing import Any, Dict, List, TypedDict

from app.core.config import settings
from app.ml.skill_gap_model import analyze_skill_gap, load_job_descriptions

try:
    from langgraph.graph import END, StateGraph
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


# ── Agent State ──────────────────────────────
class RecruitmentState(TypedDict):
    resume_text: str
    job_id: str
    candidate_name: str
    candidate_skills: List[str]
    job_title: str
    job_department: str
    required_skills: List[str]
    nice_to_have: List[str]
    fit_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    interview_email: str
    status: str
    steps: List[Dict[str, Any]]


# ── Node Functions ───────────────────────────
def parse_resume(state: RecruitmentState) -> RecruitmentState:
    """Parse resume text and extract candidate information."""
    resume_text = state["resume_text"]

    # Extract candidate name (first line or common pattern)
    lines = resume_text.strip().split("\n")
    candidate_name = lines[0].strip() if lines else "Unknown Candidate"

    # Clean up name — remove common prefixes
    for prefix in ["name:", "candidate:", "resume:", "cv:"]:
        if candidate_name.lower().startswith(prefix):
            candidate_name = candidate_name[len(prefix):].strip()

    if len(candidate_name) > 50 or len(candidate_name) < 2:
        candidate_name = "Unknown Candidate"

    # Extract skills via keyword matching
    common_skills = [
        "Python", "JavaScript", "TypeScript", "React", "Node.js", "Java", "C++",
        "SQL", "PostgreSQL", "MongoDB", "Docker", "Kubernetes", "AWS", "Azure",
        "Git", "CI/CD", "REST APIs", "GraphQL", "Machine Learning", "Data Analysis",
        "Excel", "Tableau", "Power BI", "Figma", "SEO", "SEM", "Salesforce",
        "Project Management", "Lean Six Sigma", "Agile", "Scrum",
        "Financial Modeling", "Budgeting", "GAAP", "CRM Software",
        "Leadership", "Communication", "Problem Solving", "Team Management",
        "B2B Sales", "Marketing", "Content Marketing", "HR", "Recruitment",
    ]

    text_lower = resume_text.lower()
    found_skills = [s for s in common_skills if s.lower() in text_lower]

    state["candidate_name"] = candidate_name
    state["candidate_skills"] = found_skills if found_skills else ["General Skills"]

    # Load job description details
    jds = load_job_descriptions()
    job = next((j for j in jds if j["job_id"] == state["job_id"]), None)

    if job:
        state["job_title"] = job["title"]
        state["job_department"] = job["department"]
        state["required_skills"] = job["required_skills"]
        state["nice_to_have"] = job.get("nice_to_have_skills", [])
    else:
        state["job_title"] = "Unknown Position"
        state["job_department"] = "Unknown"
        state["required_skills"] = []
        state["nice_to_have"] = []

    state["steps"].append({
        "agent": "Recruitment Agent",
        "action": f"Parsed resume for {candidate_name} — found {len(found_skills)} skills",
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
    })
    return state


def score_fit(state: RecruitmentState) -> RecruitmentState:
    """Score fitness between candidate skills and job requirements."""
    result = analyze_skill_gap(
        candidate_skills=state["candidate_skills"],
        job_required_skills=state["required_skills"],
        job_nice_to_have=state["nice_to_have"],
    )

    state["fit_score"] = result["match_score"]
    state["matched_skills"] = result["matched_skills"]
    state["missing_skills"] = result["missing_skills"]

    state["steps"].append({
        "agent": "Recruitment Agent",
        "action": f"Scored fit: {result['match_score']}% match — {len(result['matched_skills'])} skills matched",
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
    })
    return state


def rank_candidates(state: RecruitmentState) -> RecruitmentState:
    """Rank the candidate based on fit score."""
    score = state["fit_score"]

    if score >= 80:
        ranking = "Strong Fit — Recommend for interview"
    elif score >= 60:
        ranking = "Good Fit — Consider for interview"
    elif score >= 40:
        ranking = "Moderate Fit — Review with hiring manager"
    else:
        ranking = "Weak Fit — Does not meet minimum requirements"

    state["steps"].append({
        "agent": "Recruitment Agent",
        "action": f"Candidate ranking: {ranking}",
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
    })
    return state


def draft_interview_email(state: RecruitmentState) -> RecruitmentState:
    """Draft an interview invitation email."""
    name = state["candidate_name"]
    title = state["job_title"]
    dept = state["job_department"]
    score = state["fit_score"]
    matched = state["matched_skills"]

    # Try LLM
    email = _mock_interview_email(name, title, dept, matched)

    try:
        from langchain_community.chat_models import ChatOllama
        llm = ChatOllama(model=settings.OLLAMA_MODEL, base_url=settings.OLLAMA_BASE_URL, temperature=0.7)
        prompt = f"""Write a professional interview invitation email to {name} for the {title} position in {dept}.
Their strongest matching skills are: {', '.join(matched[:5])}.
Their overall fit score is {score}%.

The email should:
- Be professional and welcoming
- Mention the specific role
- Reference their relevant skills
- Propose next steps (phone screening or on-site interview)
- Be 120-150 words

Write only the email body, starting with "Dear {name},"."""

        response = llm.invoke(prompt)
        email = response.content
    except Exception:
        pass

    state["interview_email"] = email
    state["status"] = "completed"

    state["steps"].append({
        "agent": "Recruitment Agent",
        "action": "Drafted interview invitation email",
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
    })
    return state


def _mock_interview_email(name: str, title: str, dept: str, matched_skills: List[str]) -> str:
    """Generate a mock interview email."""
    skills_text = ", ".join(matched_skills[:4]) if matched_skills else "your relevant experience"

    return f"""Dear {name},

Thank you for your interest in the {title} position within our {dept} team at HRPulse Inc.

After reviewing your application, we were impressed by your background, particularly your expertise in {skills_text}. Your profile aligns well with what we are looking for, and we would love to explore this opportunity further with you.

We would like to invite you for an initial screening interview at your earliest convenience. The interview will take approximately 30 minutes and will cover your experience, technical skills, and career aspirations.

Please let us know your availability for the coming week, and we will coordinate a suitable time. You are welcome to reach out with any questions about the role or the process.

We look forward to speaking with you.

Best regards,
Talent Acquisition Team
HRPulse Inc."""


# ── Build LangGraph Workflow ─────────────────
def _build_graph():
    """Build the recruitment agent LangGraph workflow."""
    if not LANGGRAPH_AVAILABLE:
        return None

    workflow = StateGraph(RecruitmentState)

    workflow.add_node("parse_resume", parse_resume)
    workflow.add_node("score_fit", score_fit)
    workflow.add_node("rank_candidates", rank_candidates)
    workflow.add_node("draft_interview_email", draft_interview_email)

    workflow.set_entry_point("parse_resume")
    workflow.add_edge("parse_resume", "score_fit")
    workflow.add_edge("score_fit", "rank_candidates")
    workflow.add_edge("rank_candidates", "draft_interview_email")
    workflow.add_edge("draft_interview_email", END)

    return workflow.compile()


async def run_recruitment_workflow(resume_text: str, job_id: str) -> Dict:
    """Execute the full recruitment agent workflow."""
    initial_state: RecruitmentState = {
        "resume_text": resume_text,
        "job_id": job_id,
        "candidate_name": "",
        "candidate_skills": [],
        "job_title": "",
        "job_department": "",
        "required_skills": [],
        "nice_to_have": [],
        "fit_score": 0.0,
        "matched_skills": [],
        "missing_skills": [],
        "interview_email": "",
        "status": "pending",
        "steps": [],
    }

    graph = _build_graph()

    if graph is not None:
        try:
            result = graph.invoke(initial_state)
            return result
        except Exception as e:
            print(f"  [RecruitmentAgent] LangGraph execution failed: {e}")

    # Fallback: run nodes sequentially
    state = initial_state
    state = parse_resume(state)
    state = score_fit(state)
    state = rank_candidates(state)
    state = draft_interview_email(state)
    return state
