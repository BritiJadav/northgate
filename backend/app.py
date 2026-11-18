"""
Northgate Enterprise Agent - FastAPI Application
Provides RESTful APIs for KYC Agents, Governance Tracing, Model Toner,
Primary/Secondary Fallbacks, and Human-in-the-Loop Sign-offs.
"""
import os
from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from .config import config
from .auth import get_current_authenticated_user, RequireRoles, AuthUser
from .governance import governance, ActionAuditRecord, AgentTuningConfig, WarRoomDecisionRecord
from .model_gateway import model_gateway
from .data.sample_cases import SAMPLE_CASES
from .agents.ubo_extractor import ubo_agent
from .agents.gap_detector import gap_agent
from .agents.critic_agent import critic_agent

app = FastAPI(
    title="Northgate Corporate Bank - Enterprise KYC Agent Gateway",
    version="2.0.0",
    description="Enterprise API-based Agent Architecture with RBAC, Model Agility, Cost Tracing, Failover Resilience, and Critic Verification."
)

# Enable CORS for local and web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_for_static(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static") or request.url.path == "/" or request.url.path.startswith("/api/v1/governance"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# ----------------- Models / Request Schemas -----------------
class RunAgentRequest(BaseModel):
    case_id: str

class CriticVerifyRequest(BaseModel):
    case_id: str
    target_agent_id: str
    target_action_id: str
    output_text: str

class HumanSignoffRequest(BaseModel):
    action_id: str
    signoff_type: str  # "PERSON_SIGNS_1_FACTS", "PERSON_SIGNS_2_OUTREACH", "PERSON_SIGNS_3_RISK"
    decision: str      # "APPROVED", "REJECTED_REWORK"
    signer_notes: str

class FaultInjectionRequest(BaseModel):
    enabled: bool
    error_type: Optional[str] = "HTTP 429: Rate limit exceeded (50 calls/min gateway quota reached)"

class AgentTuningRequest(BaseModel):
    temperature: Optional[float] = None
    max_output_tokens: Optional[int] = None
    assigned_primary_model: Optional[str] = None
    assigned_fallback_model: Optional[str] = None
    active: Optional[bool] = None
    system_prompt_override: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    api_key: str
    username: str
    full_name: str
    role: str
    department: str
    message: str

# ----------------- Auth & User Profile -----------------
@app.post("/api/v1/auth/login", response_model=LoginResponse, tags=["Security & Auth"])
def login_with_password(req: LoginRequest):
    """
    Validates username and password, issuing session Bearer Token and Client X-API-Key.
    """
    user_cred = config.USER_CREDENTIALS.get(req.username.strip().lower())
    if not user_cred or user_cred["password"] != req.password.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Failed: Invalid username or password."
        )

    return LoginResponse(
        token=user_cred["token"],
        api_key=user_cred["api_key"],
        username=req.username,
        full_name=user_cred["full_name"],
        role=user_cred["role"],
        department=user_cred["department"],
        message=f"Authentication successful. Welcome, {user_cred['full_name']}."
    )

@app.get("/api/v1/auth/me", response_model=AuthUser, tags=["Security & Auth"])
def get_user_profile(user: AuthUser = Depends(get_current_authenticated_user)):
    """Verifies Bearer Token and X-API-Key and returns authenticated caller identity & RBAC role"""
    return user


# ----------------- Corporate Cases -----------------
@app.get("/api/v1/cases", tags=["Cases"])
def list_cases(user: AuthUser = Depends(get_current_authenticated_user)):
    """List pending corporate onboarding cases"""
    return [
        {
            "case_id": c["case_id"],
            "client_name": c["client_name"],
            "entity_type": c["entity_type"],
            "incorporation_country": c["incorporation_country"],
            "relationship_manager": c["relationship_manager"],
            "assigned_analyst": c["assigned_analyst"],
            "days_in_progress": c["days_in_progress"],
            "current_status": c["current_status"],
            "filings_count": len(c["source_filings"]),
            "screening_hits_count": len(c["raw_screening_hits"])
        }
        for c in SAMPLE_CASES.values()
    ]

@app.get("/api/v1/cases/{case_id}", tags=["Cases"])
def get_case_detail(case_id: str, user: AuthUser = Depends(get_current_authenticated_user)):
    """Retrieve full case files, registry extracts, and screening alerts"""
    case = SAMPLE_CASES.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


# ----------------- Agent Operations (Primary & Critic) -----------------
@app.post("/api/v1/agents/extract-ubos", tags=["Agents"])
def execute_ubo_extraction(
    req: RunAgentRequest,
    user: AuthUser = Depends(RequireRoles(["analyst", "ops_lead"]))
):
    """Executes UBO Extraction Agent with citations (Sarah Jenkins ownership)"""
    return ubo_agent.extract_ownership_tree(case_id=req.case_id, user=user)

@app.post("/api/v1/agents/detect-gaps", tags=["Agents"])
def execute_gap_detection(
    req: RunAgentRequest,
    user: AuthUser = Depends(RequireRoles(["analyst", "ops_lead"]))
):
    """Executes Unified Gap Detector & Outreach Compiler (Elena Gomez ownership)"""
    return gap_agent.analyze_gaps_and_draft_outreach(case_id=req.case_id, user=user)

@app.post("/api/v1/agents/verify-critic", tags=["Agents"])
def execute_critic_verification(
    req: CriticVerifyRequest,
    user: AuthUser = Depends(RequireRoles(["analyst", "ops_lead", "mlro"]))
):
    """Executes Critic Agent: Hallucination & Citation Verification (Claire Bennett ownership)"""
    return critic_agent.critique_and_verify(
        case_id=req.case_id,
        target_agent_id=req.target_agent_id,
        target_action_id=req.target_action_id,
        primary_output_text=req.output_text,
        user=user
    )


# ----------------- Human Sign-Off (Person Signs 1, 2, 3) -----------------
@app.post("/api/v1/signoff", tags=["Human-In-The-Loop"])
def record_human_signoff(
    req: HumanSignoffRequest,
    user: AuthUser = Depends(get_current_authenticated_user)
):
    """
    Enforces Northgate ADR-001: Machine proposes drafts; human signs every decision.
    Person Signs 1: Analyst confirms facts
    Person Signs 2: Analyst/RM sends outreach
    Person Signs 3: MLRO assigns risk rating
    """
    # Enforce role boundaries
    if req.signoff_type == "PERSON_SIGNS_3_RISK" and user.role not in ["mlro", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="SMCR Compliance Violation: Only an authorized MLRO (David Ross) can sign the risk rating."
        )

    # Locate action and mark signed
    for rec in governance.audit_log:
        if rec.action_id == req.action_id:
            rec.human_signoff_status = req.decision
            rec.human_signed_by = f"{user.full_name} ({user.role.upper()})"
            from datetime import datetime, timezone
            rec.human_signed_at = datetime.now(timezone.utc).isoformat()
            return {
                "message": f"Sign-off recorded: {req.decision}",
                "action_id": req.action_id,
                "signoff_type": req.signoff_type,
                "signed_by": rec.human_signed_by,
                "timestamp": rec.human_signed_at,
                "notes": req.signer_notes
            }

    raise HTTPException(status_code=404, detail=f"Action ID {req.action_id} not found in audit log")


# ----------------- Agent Toner & Model Swapping -----------------
@app.get("/api/v1/models", tags=["Agent Toner & Models"])
def list_available_models(user: AuthUser = Depends(get_current_authenticated_user)):
    """Lists registered models, provider endpoints, and pricing table"""
    return {
        "active_providers": model_gateway.providers,
        "pricing_table": config.PRICING_TABLE,
        "fault_injection_active": model_gateway.simulate_primary_outage,
        "simulated_error": model_gateway.simulate_primary_error_type
    }

@app.post("/api/v1/models/fault-injection", tags=["Scalability & Resilience"])
def toggle_fault_injection(
    req: FaultInjectionRequest,
    user: AuthUser = Depends(RequireRoles(["admin", "ops_lead", "analyst", "mlro"]))
):
    """Toggles simulated primary outage (HTTP 429) to demonstrate automatic secondary fallback"""
    model_gateway.set_fault_injection(req.enabled, req.error_type)
    return {
        "status": "success",
        "simulate_primary_outage": model_gateway.simulate_primary_outage,
        "injected_error": model_gateway.simulate_primary_error_type,
        "message": "Primary outage active. Next agent calls will automatically failover to secondary fallback model!" if req.enabled else "Primary model restored."
    }

@app.get("/api/v1/governance/agents", tags=["Governance & Tuning"])
def list_governed_agents(user: AuthUser = Depends(get_current_authenticated_user)):
    """List all agents with ownership, version, assigned primary and fallback models"""
    return list(governance.agent_configs.values())

@app.put("/api/v1/governance/agents/{agent_id}", tags=["Governance & Tuning"])
def tune_individual_agent(
    agent_id: str,
    req: AgentTuningRequest,
    user: AuthUser = Depends(RequireRoles(["admin", "ops_lead", "mlro", "analyst"]))
):
    """
    'Can I individually fix that agent?'
    Allows runtime tuning of agent model, temperature, active status, and prompts without redeploying.
    """
    try:
        updated = governance.update_agent_config(
            agent_id=agent_id,
            updates=req.model_dump(exclude_unset=True),
            updated_by=user.username
        )
        return {
            "message": f"Agent {agent_id} successfully tuned and updated.",
            "updated_config": updated
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ----------------- Governance, Tracing & Cost Observability -----------------
@app.get("/api/v1/governance/audit-log", tags=["Governance & Audit"])
def get_audit_trail(
    limit: int = 50,
    agent_id: Optional[str] = None,
    user: AuthUser = Depends(get_current_authenticated_user)
):
    """Retrieves immutable audit trail with trace IDs, token counts, costs, and failover status"""
    logs = governance.audit_log
    if agent_id:
        logs = [l for l in logs if l.agent_id == agent_id]
    return logs[:limit]

@app.get("/api/v1/governance/metrics", tags=["Governance & Audit"])
def get_governance_metrics(user: AuthUser = Depends(get_current_authenticated_user)):
    """Get aggregated cost, token consumption, latency, and agent health breakdown"""
    return governance.get_summary_metrics()

# ----------------- Virtusa Delivery Leadership War Room & Stakeholder Hub -----------------
@app.get("/api/v1/war-room/decisions", tags=["War Room & Delivery Leadership"])
def get_war_room_decisions(
    round_num: Optional[int] = None,
    user: AuthUser = Depends(get_current_authenticated_user)
):
    """Retrieves Virtusa FDE Module 8 War-Room Decision Log (All 8 Injects)"""
    return governance.get_decision_log(round_filter=round_num)

@app.post("/api/v1/war-room/decisions", tags=["War Room & Delivery Leadership"])
def add_war_room_decision(
    decision: WarRoomDecisionRecord,
    user: AuthUser = Depends(get_current_authenticated_user)
):
    """Adds a new executive decision to the live decision log"""
    return governance.add_decision(decision)

@app.get("/api/v1/war-room/stakeholder-data", tags=["War Room & Delivery Leadership"])
def get_stakeholder_views_data(user: AuthUser = Depends(get_current_authenticated_user)):
    """Unified data packet serving the 4 stakeholder dashboards from the exact same live telemetry"""
    return governance.get_stakeholder_metrics()

from fastapi.responses import RedirectResponse

# Mount frontend directory for easy serving
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/", include_in_schema=False)
def root():
    """Redirect root directly to the interactive frontend presentation pack"""
    return RedirectResponse(url="/static/index.html")

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "system": "Northgate Corporate Bank - Enterprise KYC Agent Gateway",
        "status": "OPERATIONAL",
        "api_docs": "/docs",
        "frontend_ui": "/static/index.html"
    }
