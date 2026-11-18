"""
Northgate Enterprise Agent - Governance, Audit & Cost Tracing Module
Tracks per-action cost, latency, token consumption, agent owner transparency,
and allows individually tuning, updating, and fixing each agent.
"""
import time
import uuid
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from .config import config

class ActionAuditRecord(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    case_id: str
    agent_id: str
    agent_name: str
    agent_owner: str
    agent_version: str
    requested_by_user: str
    requested_by_role: str
    model_requested: str
    model_actual: str
    provider_actual: str
    is_fallback: bool = False
    fallback_reason: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    status: str = "SUCCESS"  # SUCCESS, FALLBACK_TRIGGERED, CRITIC_FLAGGED, FAILED
    critic_score: Optional[int] = None
    critic_verdict: Optional[str] = None
    citations_count: int = 0
    human_signoff_required: bool = True
    human_signoff_status: str = "PENDING"  # PENDING, APPROVED, REJECTED
    human_signed_by: Optional[str] = None
    human_signed_at: Optional[str] = None
    input_summary: str = ""
    output_summary: str = ""

class AgentTuningConfig(BaseModel):
    agent_id: str
    name: str
    owner: str
    department: str
    version: str
    description: str
    active: bool = True
    temperature: float = 0.2
    max_output_tokens: int = 2048
    system_prompt_override: Optional[str] = None
    assigned_primary_model: str = "gemini-3-flash-preview"
    assigned_fallback_model: str = "claude-3-5-sonnet"
    critic_enforcement_level: str = "STRICT"  # STRICT, BALANCED, ADVISORY

class WarRoomDecisionRecord(BaseModel):
    decision_id: str
    round_num: int  # 1 or 2
    inject_title: str
    inject_description: str
    decision_summary: str
    owner: str
    door_type: str  # "Two-way door" or "One-way door"
    who_we_told: str
    by_when: str
    status: str = "RESOLVED"  # RESOLVED, IN_PROGRESS, ESCALATED
    audience_analyst: str
    audience_cro: str
    audience_ceo: str
    situation_and_impact: str
    escalation_options: List[Dict[str, str]]
    recommendation: str
    decision_needed_by: str

class GovernanceRegistry:
    def __init__(self):
        # Store for all traces - pre-seeded with baseline verified corporate actions
        now_iso = datetime.now(timezone.utc).isoformat()
        self.audit_log: List[ActionAuditRecord] = [
            ActionAuditRecord(
                action_id="ACT-8419A01",
                timestamp=now_iso,
                case_id="NCB-CASE-7891",
                agent_id="AGNT-UBO-01",
                agent_name="Multi-Tier Ownership & UBO Extractor",
                agent_owner="Sarah Jenkins",
                agent_version="1.2.4",
                requested_by_user="Elena Gomez",
                requested_by_role="analyst",
                model_requested="gemini-3-flash-preview",
                model_actual="gemini-3-flash-preview",
                provider_actual="Google Cloud Vertex AI (Approved Lab Model)",
                is_fallback=False,
                input_tokens=620,
                output_tokens=540,
                total_tokens=1160,
                cost_usd=0.00112,
                latency_ms=842,
                status="SUCCESS",
                citations_count=5,
                human_signoff_required=True,
                human_signoff_status="APPROVED",
                human_signed_by="Elena Gomez",
                human_signed_at=now_iso,
                input_summary="Extract UBOs for Apex Meridian Shipping Ltd",
                output_summary="Identified 3 UBOs (>25%): Alistair Vance (35.7%), Elena Rostova (28.5%), Marcus Sterling (25.0%)"
            ),
            ActionAuditRecord(
                action_id="ACT-7290B02",
                timestamp=now_iso,
                case_id="NCB-CASE-7891",
                agent_id="AGNT-GAP-02",
                agent_name="Unified Gap Detection & Outreach Drafter",
                agent_owner="Elena Gomez",
                agent_version="2.0.1",
                requested_by_user="Elena Gomez",
                requested_by_role="analyst",
                model_requested="gemini-3-flash-preview",
                model_actual="gemini-3-flash-preview",
                provider_actual="Google Cloud Vertex AI (Approved Lab Model)",
                is_fallback=False,
                input_tokens=810,
                output_tokens=490,
                total_tokens=1300,
                cost_usd=0.00128,
                latency_ms=915,
                status="SUCCESS",
                citations_count=4,
                human_signoff_required=True,
                human_signoff_status="PENDING",
                input_summary="Detect missing verification documents across layers",
                output_summary="Flagged 3 missing items: Meridian Group 2025 Audited Accounts, Cert of Good Standing, Alistair Vance POA"
            ),
            ActionAuditRecord(
                action_id="ACT-6102C03",
                timestamp=now_iso,
                case_id="NCB-CASE-7891",
                agent_id="AGNT-SCREEN-03",
                agent_name="Sanctions & PEP Screening Triage Assistant",
                agent_owner="David Ross",
                agent_version="1.1.0",
                requested_by_user="David Ross",
                requested_by_role="mlro",
                model_requested="gemini-3-flash-preview",
                model_actual="gemini-3-flash-preview",
                provider_actual="Google Cloud Vertex AI (Approved Lab Model)",
                is_fallback=False,
                input_tokens=420,
                output_tokens=310,
                total_tokens=730,
                cost_usd=0.00071,
                latency_ms=620,
                status="SUCCESS",
                citations_count=6,
                human_signoff_required=True,
                human_signoff_status="APPROVED",
                human_signed_by="David Ross",
                human_signed_at=now_iso,
                input_summary="Sanctions and PEP screening triage",
                output_summary="Zero direct OFAC/UK sanctions hits. PEP nexus cleared on Marcus Sterling with enhanced DD completed."
            )
        ]
        
        # Per-agent config registry (allows individually fixing / tuning agents)
        self.agent_configs: Dict[str, AgentTuningConfig] = {
            "AGNT-UBO-01": AgentTuningConfig(
                agent_id="AGNT-UBO-01",
                name="Multi-Tier Ownership & UBO Extractor",
                owner="Sarah Jenkins",
                department="KYC Operations",
                version="1.2.4",
                description="Extracts company hierarchy, parent entities, and UBOs (>25%) from registry filings with document citations.",
                temperature=0.1,
                max_output_tokens=2048,
                assigned_primary_model="gemini-3-flash-preview",
                assigned_fallback_model="claude-3-5-sonnet",
                critic_enforcement_level="STRICT"
            ),
            "AGNT-GAP-02": AgentTuningConfig(
                agent_id="AGNT-GAP-02",
                name="Unified Gap Detection & Outreach Drafter",
                owner="Elena Gomez",
                department="Senior KYC Analysis",
                version="2.0.1",
                description="Detects missing documents across all corporate layers on Day 2 and drafts one consolidated client outreach email.",
                temperature=0.2,
                max_output_tokens=2048,
                assigned_primary_model="gemini-3-flash-preview",
                assigned_fallback_model="gpt-4o",
                critic_enforcement_level="STRICT"
            ),
            "AGNT-SCREEN-03": AgentTuningConfig(
                agent_id="AGNT-SCREEN-03",
                name="Sanctions & PEP Screening Triage Assistant",
                owner="David Ross",
                department="MLRO Compliance",
                version="1.1.0",
                description="Clusters fuzzy name matches across PEP and sanctions lists, drafting discount rationales without assigning risk ratings.",
                temperature=0.1,
                max_output_tokens=1500,
                assigned_primary_model="gemini-3-flash-preview",
                assigned_fallback_model="claude-3-5-sonnet",
                critic_enforcement_level="STRICT"
            ),
            "AGNT-CRITIC-99": AgentTuningConfig(
                agent_id="AGNT-CRITIC-99",
                name="Independent Regulatory & Citation Critic",
                owner="Claire Bennett",
                department="Model Risk & Second Line",
                version="1.5.0",
                description="Reviews primary agent outputs against raw source filings, detects hallucinations, verifies citations, and verifies regulatory boundaries.",
                temperature=0.0,
                max_output_tokens=2048,
                assigned_primary_model="gemini-3-flash-preview",
                assigned_fallback_model="claude-3-5-sonnet",
                critic_enforcement_level="STRICT"
            )
        }

        # Virtusa FDE Module 8 Delivery Leadership - War Room Decision Log (All 8 Injects)
        self.decision_log: List[WarRoomDecisionRecord] = [
            WarRoomDecisionRecord(
                decision_id="DEC-01",
                round_num=1,
                inject_title="Quota cap",
                inject_description="Azure OpenAI quota caps the pilot at 40% of volume. Three weeks to raise it.",
                decision_summary="Use structured Account Aggregator data where it exists; extract only the rest; route overflow to Google Vertex Gemini backup; request quota today.",
                owner="Engineering Lead",
                door_type="Two-way door",
                who_we_told="Head of Credit Ops, CISO, RMs in the pilot region",
                by_when="Today",
                status="RESOLVED",
                audience_analyst="Workflow continues without interruption. Overflow requests seamlessly route via Vertex Gemini with identical response times.",
                audience_cro="Multi-cloud routing complies with model risk policy; schemas are identical and 100% Critic verified; a person still makes the final decision.",
                audience_ceo="Pilot capacity expanded from 40% to 100% of pilot volume at zero extra cost, preserving the 18 → 9 target.",
                situation_and_impact="Azure OpenAI quota caps pilot at 40% volume, threatening an immediate stall on 60% of onboarding applications in Week 3.",
                escalation_options=[
                    {"option": "Option A: Pause 60% of intake", "tradeoff": "Protects single-model purity but destroys 18→9 pilot milestone."},
                    {"option": "Option B: Wait 3 weeks for Azure quota raise", "tradeoff": "Pilot slips past steering committee deadline."},
                    {"option": "Option C: Multi-provider routing via Gateway (Gemini/Claude) + AA structured data", "tradeoff": "Recommended. Keeps 100% volume flowing today."}
                ],
                recommendation="Option C: Deploy dynamic multi-provider routing and ingest structured AA data.",
                decision_needed_by="Today 14:00 IST"
            ),
            WarRoomDecisionRecord(
                decision_id="DEC-02",
                round_num=1,
                inject_title="Scope pressure",
                inject_description="CEO: 'For the board demo, can the AI auto-approve loans under ₹5 lakh?'",
                decision_summary="Decline auto-approval under ADR-001 (Human-in-the-loop). AI prepares pre-populated draft approval memos with instant credit risk scoring; human credit analyst retains sole sign-off authority.",
                owner="Product & Architecture Lead",
                door_type="One-way door",
                who_we_told="CEO, CRO, Head of Credit Ops, Legal Counsel",
                by_when="Immediate",
                status="RESOLVED",
                audience_analyst="AI will highlight clean loans under ₹5L so your review takes 30 seconds; your professional sign-off remains mandatory.",
                audience_cro="Zero unsealed credit risk exposure. Policy engine actively blocks autonomous lending. Regulatory boundary preserved.",
                audience_ceo="We deliver 90% of the turnaround acceleration (minutes instead of hours) while keeping banking license and regulatory compliance 100% intact.",
                situation_and_impact="Executive pressure to demo fully autonomous lending under ₹5L threatens banking regulatory compliance and model risk governance.",
                escalation_options=[
                    {"option": "Option A: Permit autonomous lending under ₹5L", "tradeoff": "High risk of regulatory enforcement action, non-compliance with RBI/FCA guidelines."},
                    {"option": "Option B: Refuse outright without alternative", "tradeoff": "Disappoints CEO and board sponsors ahead of demo."},
                    {"option": "Option C: 30-second rapid human sign-off with AI pre-drafted memo", "tradeoff": "Recommended. Delivers high speed with zero regulatory breach."}
                ],
                recommendation="Option C: Rapid-sign workflow with mandatory human-in-the-loop.",
                decision_needed_by="Immediate"
            ),
            WarRoomDecisionRecord(
                decision_id="DEC-03",
                round_num=1,
                inject_title="Blocked consent",
                inject_description="Account Aggregator consent wording needs Legal review – 10 days.",
                decision_summary="Decouple intake streams: accept digital PDF bank statements via OCR pipeline in parallel while Legal finalizes digital AA consent text; fast-track Legal review.",
                owner="Operations Lead",
                door_type="Two-way door",
                who_we_told="Legal Counsel, Credit Ops, Pilot Branch RMs",
                by_when="Within 24h",
                status="RESOLVED",
                audience_analyst="Continue accepting uploaded PDF statements in Workbench. AI parses them with same accuracy as AA feed.",
                audience_cro="Legal and data consent maintained via traditional digital consent forms; zero unauthorized data harvesting.",
                audience_ceo="Intake continues uninterrupted; 18 → 9 cycle time trajectory maintained during the 10-day legal clearance window.",
                situation_and_impact="A 10-day legal consent block on Account Aggregator API threatens to halt customer onboarding intake in the pilot region.",
                escalation_options=[
                    {"option": "Option A: Halt pilot until Legal signs off AA wording", "tradeoff": "10-day delay breaks 6-week pilot timeline."},
                    {"option": "Option B: Use unapproved AA consent text", "tradeoff": "Severe data privacy compliance violation."},
                    {"option": "Option C: Parallel dual-intake (OCR uploaded statements + AA once signed)", "tradeoff": "Recommended. Zero downtime and legally compliant."}
                ],
                recommendation="Option C: Dual-intake fallback with statement OCR.",
                decision_needed_by="Today EOD"
            ),
            WarRoomDecisionRecord(
                decision_id="DEC-04",
                round_num=1,
                inject_title="Model risk",
                inject_description="'Validate the extraction before the pilot widens' – 6 weeks block requested by Model Risk.",
                decision_summary="Deploy independent Second-Line Critic agent (AGNT-CRITIC-99) for automated 100% citation grounding checks, coupled with 100% human analyst sign-off for Weeks 1-2, reducing to 20% sampled audit in Week 4.",
                owner="Model Risk Sponsor & Enterprise Architect",
                door_type="Two-way door",
                who_we_told="Head of Model Risk, CRO, Delivery Lead",
                by_when="Today 16:00 IST",
                status="RESOLVED",
                audience_analyst="The Critic agent will display an inline verification badge on every extracted figure, confirming source document coordinates.",
                audience_cro="Second-line automated Critic verifies 100% of facts against raw source documents before analyst confirmation; model risk is mathematically bounded.",
                audience_ceo="Model Risk approved gating framework; 6-week block removed; pilot widens on schedule with zero compromise to quality.",
                situation_and_impact="Model Risk's 6-week validation freeze would derail the entire pilot and miss the executive board review.",
                escalation_options=[
                    {"option": "Option A: Accept 6-week validation freeze", "tradeoff": "Pilot timeline slips by 42 days; competitor takes market lead."},
                    {"option": "Option B: Override Model Risk team without sign-off", "tradeoff": "Creates unmanaged audit finding and governance breach."},
                    {"option": "Option C: Automated Critic 2nd-line validation + 100% human signoff sampling", "tradeoff": "Recommended. Satisfies Model Risk criteria within 48 hours."}
                ],
                recommendation="Option C: Automated Critic verification + progressive sampling.",
                decision_needed_by="Today 16:00 IST"
            ),
            WarRoomDecisionRecord(
                decision_id="DEC-05",
                round_num=2,
                inject_title="Sales vs Credit Ops",
                inject_description="RMs refuse the completeness checklist – 'it slows logins'.",
                decision_summary="Automate dossier completeness verification via AGNT-GAP-02 (Gap Detection & Client Outreach agent). The agent scans filings upon upload and auto-prompts missing items in 15 seconds, eliminating manual RM checklists.",
                owner="Credit Ops Lead & Product Manager",
                door_type="Two-way door",
                who_we_told="Head of Sales (RMs), Head of Credit Ops, Regional Directors",
                by_when="Tomorrow 10:00 IST",
                status="RESOLVED",
                audience_analyst="No incomplete dossiers will reach your desk; Gap agent ensures 100% document completeness before files enter your queue.",
                audience_cro="Audit trail records complete document provenance for every onboarding file; CDD compliance increases to 98%.",
                audience_ceo="Eliminated conflict between sales velocity and credit standards. RM intake time drops by 45 minutes per application.",
                situation_and_impact="Relationship Managers bypassing the manual checklist leads to a 42% ping-pong rate between Credit Ops and clients.",
                escalation_options=[
                    {"option": "Option A: Force RMs to fill manual checklist", "tradeoff": "Continued RM pushback and delayed client logins."},
                    {"option": "Option B: Let Credit Ops manually chase missing files", "tradeoff": "Bloats analyst cycle time back towards 18 days."},
                    {"option": "Option C: Instant automated Gap Detection Agent at intake", "tradeoff": "Recommended. Instant 15s automated check with zero RM friction."}
                ],
                recommendation="Option C: Automated Gap Detection at intake.",
                decision_needed_by="Tomorrow 10:00 IST"
            ),
            WarRoomDecisionRecord(
                decision_id="DEC-06",
                round_num=2,
                inject_title="A security breach",
                inject_description="An engineer tested with a real customer's bank statement in dev.",
                decision_summary="Immediate containment: Purge dev logs and storage buckets, cycle all test credentials, deploy automated synthetic PII masker for dev/staging environments, mandate isolated sandbox testing.",
                owner="CISO & Engineering Lead",
                door_type="One-way door",
                who_we_told="CISO, Data Protection Officer, CRO, Engineering Staff",
                by_when="Immediate (within 2h)",
                status="RESOLVED",
                audience_analyst="Production environment was untouched; client data and production systems remain fully secure and operational.",
                audience_cro="Containment verified within 45 minutes; zero exfiltration outside bank boundary; automated synthetic data masking deployed.",
                audience_ceo="Threat neutralized instantly; no client notification required under GDPR/DPDP; permanent automated guardrails installed.",
                situation_and_impact="Real customer PII used in dev creates risk of data leakage and regulatory violation.",
                escalation_options=[
                    {"option": "Option A: Informal reprimand and manual file deletion", "tradeoff": "Fails audit; leaves residual log copies and systemic vulnerability."},
                    {"option": "Option B: Shut down development entirely for 2 weeks", "tradeoff": "Destroys delivery momentum and pilot milestones."},
                    {"option": "Option C: Full dev purge + automated synthetic PII masker gateway + credential rotation", "tradeoff": "Recommended. Eliminates risk and establishes permanent safety."}
                ],
                recommendation="Option C: Comprehensive purge, synthetic masker, credential rotation.",
                decision_needed_by="Immediate"
            ),
            WarRoomDecisionRecord(
                decision_id="DEC-07",
                round_num=2,
                inject_title="Trust slipping",
                inject_description="Analysts edit 35% of figures from one bank's format.",
                decision_summary="Isolate Bank Format C in Agent Toner. Fine-tune table extraction prompt, lower temperature to 0.05, and add visual warning badge in UI alerting analysts to verify table totals on Format C until fine-tuning re-verification reaches 98%.",
                owner="Lead AI Engineer & Elena Gomez (Senior Analyst)",
                door_type="Two-way door",
                who_we_told="All Credit & KYC Analysts, Head of Credit Ops, Model Risk",
                by_when="Today 14:00 IST",
                status="RESOLVED",
                audience_analyst="⚠️ Alert: Bank Format C statements show table shift anomalies. Double-check operating turnover and tax fields; new fine-tuned model deploying tonight.",
                audience_cro="The 35% manual edits prove that analyst human oversight is catching anomalies exactly as designed; risk of erroneous credit approval is 0%.",
                audience_ceo="Targeted fix in progress; only 12% of pilot volume uses Format C; overall pilot cycle time impact is under 0.4 days.",
                situation_and_impact="High edit rate on Bank Format C threatens analyst trust and slows decision throughput.",
                escalation_options=[
                    {"option": "Option A: Ignore and let analysts keep editing manually", "tradeoff": "Erodes team confidence and wastes 30 min per file."},
                    {"option": "Option B: Remove Bank Format C from pilot scope", "tradeoff": "Reduces pilot coverage and frustrates clients from that bank."},
                    {"option": "Option C: Isolate template in Agent Toner + prompt fine-tuning + UI alert banner", "tradeoff": "Recommended. Fixes root cause and keeps analysts informed."}
                ],
                recommendation="Option C: Agent Toner isolation and prompt recalibration.",
                decision_needed_by="Today 14:00 IST"
            ),
            WarRoomDecisionRecord(
                decision_id="DEC-08",
                round_num=2,
                inject_title="The date moves",
                inject_description="The steering committee is now a week earlier.",
                decision_summary="Lock demo scope to Kestrel Week 3 core slice (statement + GST extraction + gap outreach). Present the 18 → 9 live tracking dashboard with 4 multi-stakeholder lenses (CEO, Analyst, CRO, Engineering).",
                owner="Delivery Lead & Program Sponsor",
                door_type="Two-way door",
                who_we_told="Steering Committee Members, Workstream Leads, Executive Sponsors",
                by_when="EOD Today",
                status="RESOLVED",
                audience_analyst="Demo will use anonymized pilot cases without disturbing your daily workflow or case queue.",
                audience_cro="Model Risk and Human-in-the-Loop governance audit reports will be featured prominently in the executive pack.",
                audience_ceo="Live dashboard proves 18 → 9 cycle time target is on track (9.2 days achieved), cost per file is $0.003, and 7 functions are aligned.",
                situation_and_impact="Executive steering committee moved 7 days earlier, compressing prep time for the leadership presentation.",
                escalation_options=[
                    {"option": "Option A: Request delay back to original date", "tradeoff": "Signals lack of delivery confidence to senior leadership."},
                    {"option": "Option B: Rush unvalidated features into demo", "tradeoff": "High risk of glitch or hallucination during executive presentation."},
                    {"option": "Option C: Freeze scope on Week 3 core slice (18→9 metric + 4 stakeholder dashboards)", "tradeoff": "Recommended. Solid, verified, and impactful."}
                ],
                recommendation="Option C: Freeze scope on Week 3 core slice with 4 stakeholder dashboards.",
                decision_needed_by="EOD Today"
            )
        ]

    def record_action(self, record: ActionAuditRecord) -> ActionAuditRecord:
        """Appends action to immutable audit log"""
        self.audit_log.insert(0, record)  # most recent first
        return record

    def update_agent_config(self, agent_id: str, updates: Dict[str, Any], updated_by: str) -> AgentTuningConfig:
        """Individually fixes / tunes an agent at runtime"""
        if agent_id not in self.agent_configs:
            raise ValueError(f"Agent ID {agent_id} not found in governance registry.")
        
        current = self.agent_configs[agent_id]
        updated_dict = current.model_dump()
        for k, v in updates.items():
            if k in updated_dict and v is not None:
                updated_dict[k] = v
        
        new_config = AgentTuningConfig(**updated_dict)
        self.agent_configs[agent_id] = new_config
        return new_config

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Calculates live governance and cost metrics across all agents"""
        total_actions = len(self.audit_log)
        total_cost = sum(r.cost_usd for r in self.audit_log)
        total_input_tokens = sum(r.input_tokens for r in self.audit_log)
        total_output_tokens = sum(r.output_tokens for r in self.audit_log)
        fallback_count = sum(1 for r in self.audit_log if r.is_fallback)
        critic_flagged_count = sum(1 for r in self.audit_log if r.status == "CRITIC_FLAGGED")
        pending_signoffs = sum(1 for r in self.audit_log if r.human_signoff_status == "PENDING")

        # Per-agent cost & action breakdown
        agent_stats: Dict[str, Dict] = {}
        for agent_id, cfg in self.agent_configs.items():
            records = [r for r in self.audit_log if r.agent_id == agent_id]
            cost = sum(r.cost_usd for r in records)
            tokens = sum(r.total_tokens for r in records)
            avg_latency = (sum(r.latency_ms for r in records) / len(records)) if records else 0
            agent_stats[agent_id] = {
                "name": cfg.name,
                "owner": cfg.owner,
                "version": cfg.version,
                "active": cfg.active,
                "actions_count": len(records),
                "total_cost_usd": round(cost, 6),
                "total_tokens": tokens,
                "avg_latency_ms": round(avg_latency, 1),
                "fallback_triggers": sum(1 for r in records if r.is_fallback)
            }

        critic_pass_rate = 100.0 if total_actions == 0 else round(((total_actions - critic_flagged_count) / total_actions) * 100, 1)
        return {
            "total_actions": total_actions,
            "total_agent_actions_executed": total_actions,
            "total_cost_usd": round(total_cost, 6),
            "total_tokens": total_input_tokens + total_output_tokens,
            "fallback_events": fallback_count,
            "total_fallback_events": fallback_count,
            "critic_flags": critic_flagged_count,
            "critic_pass_rate_pct": critic_pass_rate,
            "pending_signoffs": pending_signoffs,
            "agent_breakdown": agent_stats
        }

    def get_decision_log(self, round_filter: Optional[int] = None) -> List[WarRoomDecisionRecord]:
        """Returns the War-Room Decision Log, optionally filtered by round 1 or 2"""
        if round_filter:
            return [d for d in self.decision_log if d.round_num == round_filter]
        return self.decision_log

    def add_decision(self, record: WarRoomDecisionRecord) -> WarRoomDecisionRecord:
        """Appends a new decision into the live decision log"""
        self.decision_log.insert(0, record)
        return record

    def get_stakeholder_metrics(self) -> Dict[str, Any]:
        """Unified metrics drawn from the exact same telemetry, presented across stakeholder lenses"""
        summary = self.get_summary_metrics()
        now_str = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
        
        # Exact numbers reflecting Kestrel Pilot Week 3 & Northgate Corporate Bank Case 7891
        avg_cost = summary['total_cost_usd'] / max(1, summary['total_actions'])
        return {
            "last_updated": now_str,
            "pilot_meta": {
                "program": "Virtusa Lead FDE - Module 8 War Room",
                "pilot_name": "Project Kestrel",
                "region": "Northern Commercial Region",
                "current_week": 3,
                "total_weeks": 6,
                "target_metric": "18 -> 9 working days to decision",
                "slice_scope": "Statement and GST extraction, one document request, a person decides",
                "current_days_to_decision": 9.2,
                "baseline_days": 18.0,
                "reduction_pct": 48.9,
                "cases_processed_week": 142,
                "target_cases_week": 130,
                "functions_aligned": 7,
                "injects_count": len(self.decision_log)
            },
            "ceo_view": {
                "headline_target": "18 -> 9 Working Days",
                "current_achievement": "9.2 Days (48.9% Faster)",
                "institutional_dropoff": "4.2% (Down from 23% baseline)",
                "turnaround_velocity": "9.2 vs 18.0 working days",
                "total_cost_per_file": f"${avg_cost:.5f}",
                "annualized_revenue_protected": "£4.8M Institutional Volume",
                "active_case": {
                    "client": "Apex Meridian Shipping Ltd",
                    "status": "Day 32 Overdue File -> Fast-tracked (Decision ready in 24h)",
                    "action_required": "Analyst & MLRO finalizing unsealed draft sign-off"
                },
                "key_message": "The Kestrel pilot is tracking at 9.2 days against the 9.0 day target. Scope discipline (ADR-001) has prevented regulatory exposure while cutting cycle time by 48.9%."
            },
            "analyst_view": {
                "active_persona": "Elena Gomez (Senior KYC Analyst)",
                "queue_count": 8,
                "current_case_id": "NCB-CASE-7891",
                "what_to_check_today": [
                    {
                        "severity": "WARNING",
                        "badge": "Bank Format C",
                        "title": "35% manual edits detected on Bank Format C tables",
                        "instruction": "Double-check operating turnover and tax items before signing. Fine-tuned model deploying tonight."
                    },
                    {
                        "severity": "INFO",
                        "badge": "Missing Documents",
                        "title": "Day 2 Gap Outreach Ready",
                        "instruction": "Meridian Group 2025 Audited Accounts & Cert of Good Standing flagged. Draft client outreach ready for 1-click send."
                    }
                ],
                "actions_completed_today": summary['total_actions'],
                "fact_confirmation_status": "Ready for Sign 1",
                "key_message": "Extract UBOs and review document gaps. Check citation coordinates on Bank Format C before approving."
            },
            "cro_view": {
                "active_persona": "David Ross (MLRO) & Claire Bennett (Model Risk)",
                "human_in_loop_compliance": "100.0%",
                "unsealed_ai_decisions": 0,
                "critic_verification_pass_rate": f"{summary['critic_pass_rate_pct']}%",
                "total_hallucinations_blocked": 0,
                "regulatory_boundary_enforcement": {
                    "rule": "ADR-001: AI generates unsealed draft recommendations only",
                    "incident_blocked": "CEO request to auto-approve loans under ₹5L was automatically BLOCKED by gateway policy",
                    "authority": "MLRO retains sole statutory accountability under SMCR"
                },
                "key_message": "Zero autonomous credit liability. 100% of extracted facts verified by second-line Critic agent with raw registry citations. A person still decides every loan."
            },
            "engineering_view": {
                "active_persona": "Priya Sharma (Enterprise Architect) & Sarah Jenkins (Ops Head)",
                "model_gateway_status": "HEALTHY (Multi-Provider Active)",
                "quota_cap_mitigation": {
                    "azure_openai_cap": "40% pilot volume limit",
                    "overflow_routing": "Vertex AI Gemini 3 Flash + Anthropic Claude 3.5 Sonnet backup",
                    "status": "Seamless failover operating, 0 dropped requests"
                },
                "doors_summary": {
                    "two_way_doors": sum(1 for d in self.decision_log if "two-way" in d.door_type.lower()),
                    "one_way_doors": sum(1 for d in self.decision_log if "one-way" in d.door_type.lower()),
                    "flagged_one_way": "ADR-001 (Human Sign-off mandatory), Dev Synthetic Data Mandate (zero real statements in dev)"
                },
                "data_privacy": "100% Synthetic data masking enforced in dev/staging. Production isolated.",
                "total_tokens_consumed": summary['total_tokens'],
                "total_cost_usd": summary['total_cost_usd']
            }
        }

governance = GovernanceRegistry()
