"""
Northgate Enterprise Agent - Unified Gap Detector & Outreach Compiler
Owner: Elena Gomez (Senior KYC Analyst)
Compares extracted corporate entities against Northgate KYC Policy (Section 6).
Discovers every gap upfront on Day 2 and pre-drafts ONE consolidated outreach email
for human review (Person Signs 2: Analyst/RM sends).
"""
import json
from typing import Dict, Any
from .base import BaseEnterpriseAgent
from ..auth import AuthUser
from ..data.sample_cases import SAMPLE_CASES

class GapDetectionAgent(BaseEnterpriseAgent):
    def __init__(self):
        super().__init__(agent_id="AGNT-GAP-02")

    def analyze_gaps_and_draft_outreach(self, case_id: str, user: AuthUser) -> Dict[str, Any]:
        case = SAMPLE_CASES.get(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found.")

        prompt = f"Perform complete gap analysis across all tiers for {case['client_name']} and compile 1-shot outreach email."
        system_instruction = (
            "You are the Northgate Gap Detector Agent. Your mission is 'See every gap at the start'. "
            "Examine the 14-year archive to avoid re-requesting existing documents. "
            "Output the specific missing requirements and draft an outreach email for Relationship Manager review."
        )

        def mock_generator(is_fallback: bool, model_name: str):
            content = {
                "case_id": case_id,
                "client_name": case["client_name"],
                "gaps_summary": {
                    "total_gaps_found": 2,
                    "documents_found_in_archive": 2,
                    "outreach_cycles_needed": 1
                },
                "itemized_findings": [
                    {
                        "category": "Identity Verification (UBO)",
                        "target_entity": "Alistair Finch (UBO - 26%)",
                        "status": "MISSING_REQUIRED_DOCUMENT",
                        "policy_rule": "Northgate KYC Policy Sec 6.2 (Certified Passport Copy & Proof of Address within 90 days)",
                        "archive_check": "Not found in \\\\london-fs02\\ historic repository",
                        "action_required": "Request certified passport copy + recent utility bill"
                    },
                    {
                        "category": "Corporate Documentation",
                        "target_entity": "Meridian Holdings B.V. (Netherlands)",
                        "status": "MISSING_REQUIRED_DOCUMENT",
                        "policy_rule": "Articles of Association Clause 7.1 & KYC Policy Sec 4.1",
                        "archive_check": "Certificate of Incumbency expired in 2021",
                        "action_required": "Request fresh Certificate of Incumbency dated within 12 months"
                    },
                    {
                        "category": "Identity Verification (Director)",
                        "target_entity": "Captain Robert Sterling (Director & Beneficiary)",
                        "status": "SATISFIED_FROM_ARCHIVE",
                        "policy_rule": "KYC Policy Sec 6.1 (Director Passport)",
                        "archive_check": "Found in archive ARC-2019-MERIDIAN-01 (Valid until Nov 2028). DO NOT RE-REQUEST FROM CLIENT.",
                        "action_required": "None (Reused existing verified bank record)"
                    }
                ],
                "draft_client_outreach_email": {
                    "to": "client-onboarding@apexmeridian.com",
                    "cc": "mark.vance@northgate.com (Relationship Manager)",
                    "subject": "Northgate Corporate Bank - CDD Onboarding Requirements: Apex Meridian Shipping Ltd",
                    "status": "UNSEALED DRAFT - REQUIRES RELATIONSHIP MANAGER REVIEW (PERSON SIGNS 2)",
                    "body": (
                        "Dear Captain Sterling and the Apex Meridian Onboarding Team,\n\n"
                        "Thank you for partnering with Northgate Corporate Bank. To finalize account opening "
                        "and ensure you hit your requested target go-live date, our review across all corporate "
                        "layers requires only the following two remaining items:\n\n"
                        "1. Certified Passport copy and Proof of Residential Address (dated within last 3 months) "
                        "for Beneficial Owner Mr. Alistair Finch (26% shareholder via Pacific Crest Oceanic Pte Ltd).\n"
                        "2. A current Certificate of Incumbency for Meridian Holdings B.V. (Netherlands) dated within the last 12 months.\n\n"
                        "Please note: We have already retrieved and validated the passport records and trust documentation "
                        "for Captain Robert Sterling from our records, so no further submission is needed for him.\n\n"
                        "Submitting these items in a single packet will allow our MLRO to approve the file directly.\n\n"
                        "Warm regards,\n"
                        "Mark Vance (Corporate Coverage) & Elena Gomez (KYC Operations)\n"
                        "Northgate Corporate Bank"
                    )
                }
            }
            raw_text = json.dumps(content, indent=2)
            in_tokens = 740
            out_tokens = 680
            return raw_text, in_tokens, out_tokens

        result = self.execute_with_governance(
            case_id=case_id,
            user=user,
            prompt=prompt,
            system_instruction=system_instruction,
            mock_generator=mock_generator,
            input_summary=f"Detect gaps & compile consolidated outreach for {case['client_name']}",
            citations_count=3
        )
        return result

gap_agent = GapDetectionAgent()
