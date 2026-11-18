"""
Northgate Enterprise Agent - UBO Extraction Agent
Owner: Sarah Jenkins (Head of KYC Operations)
Presents extracted ownership chain down to Ultimate Beneficial Owners (>25%)
with exact document citations for analyst verification (Person Signs 1).
"""
from typing import Dict, Any, List
from .base import BaseEnterpriseAgent
from ..auth import AuthUser
from ..data.sample_cases import SAMPLE_CASES

class UBOExtractionAgent(BaseEnterpriseAgent):
    def __init__(self):
        super().__init__(agent_id="AGNT-UBO-01")

    def extract_ownership_tree(self, case_id: str, user: AuthUser) -> Dict[str, Any]:
        case = SAMPLE_CASES.get(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found.")

        prompt = f"Analyze registry filings for {case['client_name']} and extract all tiers down to UBOs >25% with source citations."
        system_instruction = (
            "You are an expert KYC analyst co-pilot for Northgate Corporate Bank. "
            "Extract the ownership structure, calculate effective percentage, and cite document sources for each fact. "
            "NEVER assign a final risk rating; keep output as an unsealed draft."
        )

        def mock_generator(is_fallback: bool, model_name: str):
            prefix = "[Secondary Fallback Execution] " if is_fallback else ""
            content = {
                "client_name": case["client_name"],
                "target_company": "Apex Meridian Shipping Ltd (UK #08941235)",
                "ownership_chain": [
                    {
                        "tier": "Tier 1 (Direct Shareholder - 100.0%)",
                        "entity_name": "Meridian Holdings B.V.",
                        "jurisdiction": "Netherlands (KVK: 74219902)",
                        "citation": "[Doc: UK_Companies_House_PSC_Register.pdf, Page 1]"
                    },
                    {
                        "tier": "Tier 2A (Intermediate Shareholder - 65.0% of Tier 1)",
                        "entity_name": "Pacific Crest Oceanic Pte Ltd",
                        "jurisdiction": "Singapore (ACRA: 201829104K)",
                        "citation": "[Doc: KVK_Netherlands_Extract_Meridian_BV.pdf, Dossier 74219902]"
                    },
                    {
                        "tier": "Tier 2B (Intermediate Shareholder - 35.0% of Tier 1)",
                        "entity_name": "Sterling Maritime Trust",
                        "jurisdiction": "Guernsey (Reg: GT-4410)",
                        "citation": "[Doc: KVK_Netherlands_Extract_Meridian_BV.pdf, Dossier 74219902]"
                    }
                ],
                "ubos_identified": [
                    {
                        "name": "Chen Wei-Ming",
                        "effective_percentage": "39.0% (60% of 65%)",
                        "qualifies_as_ubo": True,
                        "status": "QUALIFIED UBO (>25% statutory threshold)",
                        "citation": "[Doc: ACRA_Singapore_Profile_PacificCrest.pdf, UEN: 201829104K]"
                    },
                    {
                        "name": "Alistair Finch",
                        "effective_percentage": "26.0% (40% of 65%)",
                        "qualifies_as_ubo": True,
                        "status": "QUALIFIED UBO (>25% statutory threshold)",
                        "citation": "[Doc: ACRA_Singapore_Profile_PacificCrest.pdf, UEN: 201829104K]"
                    },
                    {
                        "name": "Captain Robert Sterling",
                        "effective_percentage": "35.0% (Via Sterling Maritime Trust)",
                        "qualifies_as_ubo": True,
                        "status": "QUALIFIED BENEFICIARY / DIRECTOR",
                        "citation": "[Doc: Northgate_14Yr_Archive_Search_LondonFS02.txt, Folder ARC-2019-MERIDIAN-01]"
                    }
                ],
                "regulatory_note": "Draft ownership tree prepared for analyst verification. MLRO sign-off required before onboarding approval."
            }
            import json
            raw_text = json.dumps(content, indent=2)
            in_tokens = 620
            out_tokens = 540
            return raw_text, in_tokens, out_tokens

        result = self.execute_with_governance(
            case_id=case_id,
            user=user,
            prompt=prompt,
            system_instruction=system_instruction,
            mock_generator=mock_generator,
            input_summary=f"Extract UBOs for {case['client_name']}",
            citations_count=5
        )
        return result

ubo_agent = UBOExtractionAgent()
