"""
HRPulse — Onboarding Agent (LangGraph Workflow)
Pipeline: generate_checklist → assign_buddy → setup_it → create_plan

Input: employee name, role, department, start date
Output: 30/60/90 day plan, IT checklist, buddy assignment, welcome email
"""

import random
from datetime import datetime
from typing import Any, Dict, List, TypedDict

from app.core.config import settings

try:
    from langgraph.graph import END, StateGraph
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


# ── Agent State ──────────────────────────────
class OnboardingState(TypedDict):
    employee_name: str
    role: str
    department: str
    start_date: str
    plan_30_60_90: Dict[str, List[str]]
    it_checklist: List[str]
    buddy_name: str
    buddy_role: str
    welcome_email: str
    status: str
    steps: List[Dict[str, Any]]


# ── Department-specific data ─────────────────
DEPT_BUDDIES = {
    "Engineering": [
        ("Arjun Mehta", "Senior Software Engineer"),
        ("Sarah Chen", "Tech Lead"),
        ("David Kim", "Platform Engineer"),
    ],
    "Sales": [
        ("Rajesh Kumar", "Regional Sales Lead"),
        ("James Wilson", "Account Executive"),
        ("Vikram Singh", "Sales Manager"),
    ],
    "Marketing": [
        ("Emily Rodriguez", "Digital Marketing Manager"),
        ("Neha Gupta", "Marketing Executive"),
        ("Fatima Al-Hassan", "Brand Strategist"),
    ],
    "HR": [
        ("Priya Sharma", "HR Business Partner"),
        ("Sneha Reddy", "People Ops Specialist"),
        ("Kavitha Nair", "Talent Acquisition Lead"),
    ],
    "Finance": [
        ("Michael Thompson", "Senior Analyst"),
        ("Robert Garcia", "Finance Manager"),
        ("Lisa Chang", "VP Finance"),
    ],
    "Operations": [
        ("Aisha Patel", "Operations Manager"),
        ("Alex Turner", "Director of Operations"),
        ("Rahul Deshmukh", "Senior Operations Manager"),
    ],
}

DEPT_PLANS = {
    "Engineering": {
        "30_days": [
            "Complete development environment setup (IDE, Git, Docker, CI/CD access)",
            "Review codebase architecture documentation and system design docs",
            "Pair program with buddy on 2-3 starter tasks or bug fixes",
            "Attend all team standups and sprint ceremonies",
            "Complete security training and code review guidelines",
            "Meet with engineering manager for role expectations walkthrough",
            "Submit first pull request for review",
        ],
        "60_days": [
            "Own a small feature end-to-end (design → implement → test → deploy)",
            "Conduct your first code review for a teammate",
            "Present a technical topic at the weekly engineering sync",
            "Shadow on-call rotation and review incident runbooks",
            "Complete at least one internal training course or certification",
            "Participate in sprint planning and estimation sessions",
        ],
        "90_days": [
            "Lead the development of a medium-complexity feature independently",
            "Contribute to architectural decisions and design reviews",
            "Mentor a newer team member or intern",
            "Deliver a 90-day retrospective presentation to your manager",
            "Set personal OKRs aligned with team and company objectives",
            "Identify one process improvement and propose implementation",
        ],
    },
    "Sales": {
        "30_days": [
            "Complete CRM (Salesforce) training and account configuration",
            "Shadow 10 client calls with senior account managers",
            "Study all product offerings, pricing, and competitive landscape",
            "Review top 20 accounts in your territory",
            "Complete objection handling and negotiation training modules",
            "Meet with cross-functional partners (Marketing, Product, CS)",
        ],
        "60_days": [
            "Manage your first 5 accounts independently",
            "Build a pipeline of at least 15 qualified opportunities",
            "Deliver your first product demo to a prospect",
            "Achieve first month's activity targets (calls, emails, meetings)",
            "Create territory plan and present to regional manager",
            "Attend one industry event or webinar",
        ],
        "90_days": [
            "Close your first deal and complete full sales cycle",
            "Maintain pipeline coverage of 3x monthly quota",
            "Develop and execute account plans for top 10 accounts",
            "Present 90-day results and Q2 strategy to leadership",
            "Establish referral network with at least 3 customer advocates",
            "Set personal OKRs aligned with revenue targets",
        ],
    },
    "Marketing": {
        "30_days": [
            "Review brand guidelines, tone of voice, and content strategy",
            "Get access to all marketing tools (Analytics, CMS, Social, Email)",
            "Audit current campaigns and performance metrics",
            "Meet with stakeholders across Sales, Product, and Design",
            "Complete SEO/SEM certification if applicable",
            "Shadow campaign launches with senior team members",
        ],
        "60_days": [
            "Plan and execute your first campaign independently",
            "Publish 4-6 content pieces (blog posts, social, email)",
            "Set up A/B tests on at least one channel",
            "Create a monthly marketing performance report",
            "Contribute to the content calendar for the next quarter",
            "Present campaign results to the marketing team",
        ],
        "90_days": [
            "Own a full marketing channel or campaign vertical",
            "Demonstrate measurable impact on lead generation or engagement",
            "Propose and pitch a new marketing initiative",
            "Deliver 90-day retrospective with KPIs and learnings",
            "Build cross-departmental relationships for co-marketing",
            "Set personal OKRs aligned with marketing objectives",
        ],
    },
    "HR": {
        "30_days": [
            "Complete HRIS system training (Workday/SuccessFactors access)",
            "Review all HR policies, handbooks, and compliance documents",
            "Shadow employee relations cases with senior HR partner",
            "Meet with department heads to understand business needs",
            "Complete employment law refresher training",
            "Familiarize yourself with benefits administration processes",
        ],
        "60_days": [
            "Handle your first employee relations case independently",
            "Support the quarterly performance review cycle",
            "Conduct your first new hire orientation session",
            "Begin workforce planning analysis for assigned business units",
            "Propose one improvement to an HR process or policy",
            "Attend an HR industry webinar or local HR community event",
        ],
        "90_days": [
            "Serve as primary HR point of contact for assigned departments",
            "Design and launch a talent development initiative",
            "Present workforce analytics and trends to leadership",
            "Deliver 90-day retrospective with impact metrics",
            "Contribute to the annual compensation review process",
            "Set personal OKRs aligned with people strategy",
        ],
    },
    "Finance": {
        "30_days": [
            "Complete ERP system training and gain financial reporting access",
            "Review chart of accounts, reporting structure, and GAAP policies",
            "Shadow month-end close process with senior team",
            "Meet with department heads to understand budget structures",
            "Complete internal audit and compliance training",
            "Familiarize with financial models and forecast templates",
        ],
        "60_days": [
            "Prepare your first monthly financial report independently",
            "Conduct variance analysis for 1-2 cost centers",
            "Support quarterly forecasting and budget revisions",
            "Build or refine a financial model for a business initiative",
            "Present findings to finance leadership",
            "Begin FP&A analysis for assigned business units",
        ],
        "90_days": [
            "Own end-to-end financial reporting for assigned areas",
            "Lead budget planning conversations with department stakeholders",
            "Identify cost optimization opportunities (target: $50K+ savings)",
            "Deliver 90-day retrospective with analytical contributions",
            "Develop scenario models for strategic initiatives",
            "Set personal OKRs aligned with finance team goals",
        ],
    },
    "Operations": {
        "30_days": [
            "Complete operations systems and tool training (Jira, Asana, ERP)",
            "Review all SOPs, process documentation, and vendor contracts",
            "Shadow operations team on daily workflow management",
            "Map current processes and identify initial improvement areas",
            "Meet with cross-functional teams (IT, Facilities, Procurement)",
            "Complete Six Sigma or project management refresher if needed",
        ],
        "60_days": [
            "Manage your first operational project independently",
            "Implement one process improvement and measure impact",
            "Establish KPI dashboards for your operational areas",
            "Conduct vendor review and negotiate at least one contract",
            "Lead a cross-functional team meeting or project standup",
            "Present an operational efficiency report to leadership",
        ],
        "90_days": [
            "Own full operational workflow for assigned areas",
            "Deliver measurable efficiency improvements (target: 10%+ improvement)",
            "Lead a significant operational project or facility initiative",
            "Deliver 90-day retrospective with operational KPIs",
            "Develop SOPs for any undocumented processes",
            "Set personal OKRs aligned with operations strategy",
        ],
    },
}


# ── Node Functions ───────────────────────────
def generate_checklist(state: OnboardingState) -> OnboardingState:
    """Generate 30/60/90 day onboarding plan based on role and department."""
    dept = state["department"]
    role = state["role"]

    plan = DEPT_PLANS.get(dept, DEPT_PLANS["Engineering"])

    # Try LLM enhancement
    try:
        from langchain_community.chat_models import ChatOllama
        llm = ChatOllama(model=settings.OLLAMA_MODEL, base_url=settings.OLLAMA_BASE_URL, temperature=0.5)
        prompt = f"""Customize this 30/60/90 day onboarding plan for a {role} in the {dept} department.
Add 1-2 role-specific items to each period. Keep existing items and just add to them.
Return only the new items, one per line, prefixed with the period (30/60/90):

30: [new item for days 1-30]
60: [new item for days 31-60]
90: [new item for days 61-90]"""

        response = llm.invoke(prompt)
        lines = response.content.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("30:"):
                plan["30_days"].append(line[3:].strip())
            elif line.startswith("60:"):
                plan["60_days"].append(line[3:].strip())
            elif line.startswith("90:"):
                plan["90_days"].append(line[3:].strip())
    except Exception:
        pass

    state["plan_30_60_90"] = plan

    state["steps"].append({
        "agent": "Onboarding Agent",
        "action": f"Generated 30/60/90 day plan for {role} in {dept}",
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
    })
    return state


def assign_buddy(state: OnboardingState) -> OnboardingState:
    """Assign an onboarding buddy from the same department."""
    dept = state["department"]
    buddies = DEPT_BUDDIES.get(dept, DEPT_BUDDIES["Engineering"])
    buddy = random.choice(buddies)

    state["buddy_name"] = buddy[0]
    state["buddy_role"] = buddy[1]

    state["steps"].append({
        "agent": "Onboarding Agent",
        "action": f"Assigned buddy: {buddy[0]} ({buddy[1]})",
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
    })
    return state


def setup_it(state: OnboardingState) -> OnboardingState:
    """Generate IT setup checklist."""
    dept = state["department"]

    base_checklist = [
        "Provision company laptop (MacBook Pro / ThinkPad)",
        "Create corporate email account and calendar",
        "Set up Slack/Teams workspace access",
        "Configure VPN and network access credentials",
        "Issue security badge and building access card",
        "Enroll in multi-factor authentication (MFA)",
        "Set up password manager (1Password/LastPass)",
        "Provision shared drive and cloud storage access",
    ]

    dept_specific = {
        "Engineering": [
            "Install development tools (VS Code, Docker, Git)",
            "Grant GitHub/GitLab repository access",
            "Configure CI/CD pipeline access",
            "Set up cloud platform credentials (AWS/Azure)",
            "Provision staging/development database access",
        ],
        "Sales": [
            "Configure Salesforce CRM account and permissions",
            "Set up Zoom/Teams for client calls",
            "Install LinkedIn Sales Navigator",
            "Grant access to sales collateral and pricing sheets",
        ],
        "Marketing": [
            "Set up Google Analytics and Search Console access",
            "Configure marketing automation platform (HubSpot)",
            "Grant social media management tool access",
            "Install design tools (Figma/Canva/Adobe CC)",
        ],
        "HR": [
            "Configure HRIS system access (Workday/SuccessFactors)",
            "Grant ATS (Applicant Tracking System) access",
            "Set up benefits administration portal",
            "Provision employee records database access",
        ],
        "Finance": [
            "Configure ERP system access (SAP/Oracle)",
            "Set up financial reporting tools",
            "Grant accounting software access",
            "Install Excel add-ins and financial modeling tools",
        ],
        "Operations": [
            "Configure project management tools (Jira/Asana)",
            "Set up supply chain management system access",
            "Grant vendor management portal access",
            "Install process mapping tools (Visio/Lucidchart)",
        ],
    }

    full_checklist = base_checklist + dept_specific.get(dept, [])
    state["it_checklist"] = full_checklist

    state["steps"].append({
        "agent": "Onboarding Agent",
        "action": f"Generated IT checklist with {len(full_checklist)} items",
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
    })
    return state


def create_plan(state: OnboardingState) -> OnboardingState:
    """Create the welcome email for the new employee."""
    name = state["employee_name"]
    role = state["role"]
    dept = state["department"]
    start_date = state["start_date"]
    buddy = state["buddy_name"]
    buddy_role = state["buddy_role"]

    welcome_email = f"""Dear {name},

Welcome to HRPulse! We are thrilled to have you join us as a {role} in our {dept} team, starting {start_date}.

Here's what to expect on your first day:

🕘 Start Time: 9:00 AM
📍 Location: HRPulse HQ, Floor 4 — or virtual via the link in your calendar invite
👋 Your Onboarding Buddy: {buddy} ({buddy_role}) will be your go-to person for questions, introductions, and getting settled in. They'll reach out before your start date to introduce themselves.

First Week Highlights:
  • Day 1: Orientation, IT setup, team introductions, and office tour
  • Day 2: Deep dive into our products, culture, and values
  • Day 3-5: Begin your 30-day onboarding plan with hands-on training

What to Bring:
  • Government-issued photo ID (for security badge)
  • Banking details for payroll setup
  • Any dietary preferences for your welcome lunch!

Your onboarding portal will be shared on Day 1 with your complete 30/60/90 day plan, IT setup checklist, and all relevant resources.

We've been looking forward to having you on the team, and we're confident you'll make a great impact here.

If you have any questions before your start date, don't hesitate to reach out to our HR team at hr@hrpulse.com.

See you soon!

Warm regards,
The HRPulse Team"""

    state["welcome_email"] = welcome_email
    state["status"] = "completed"

    state["steps"].append({
        "agent": "Onboarding Agent",
        "action": "Generated welcome email and finalized onboarding package",
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
    })
    return state


# ── Build LangGraph Workflow ─────────────────
def _build_graph():
    """Build the onboarding agent LangGraph workflow."""
    if not LANGGRAPH_AVAILABLE:
        return None

    workflow = StateGraph(OnboardingState)

    workflow.add_node("generate_checklist", generate_checklist)
    workflow.add_node("assign_buddy", assign_buddy)
    workflow.add_node("setup_it", setup_it)
    workflow.add_node("create_plan", create_plan)

    workflow.set_entry_point("generate_checklist")
    workflow.add_edge("generate_checklist", "assign_buddy")
    workflow.add_edge("assign_buddy", "setup_it")
    workflow.add_edge("setup_it", "create_plan")
    workflow.add_edge("create_plan", END)

    return workflow.compile()


async def run_onboarding_workflow(
    employee_name: str,
    role: str,
    department: str,
    start_date: str,
) -> Dict:
    """Execute the full onboarding agent workflow."""
    initial_state: OnboardingState = {
        "employee_name": employee_name,
        "role": role,
        "department": department,
        "start_date": start_date,
        "plan_30_60_90": {},
        "it_checklist": [],
        "buddy_name": "",
        "buddy_role": "",
        "welcome_email": "",
        "status": "pending",
        "steps": [],
    }

    graph = _build_graph()

    if graph is not None:
        try:
            result = graph.invoke(initial_state)
            return result
        except Exception as e:
            print(f"  [OnboardingAgent] LangGraph execution failed: {e}")

    # Fallback
    state = initial_state
    state = generate_checklist(state)
    state = assign_buddy(state)
    state = setup_it(state)
    state = create_plan(state)
    return state
