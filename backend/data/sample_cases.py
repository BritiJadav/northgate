"""
Northgate Enterprise Agent - Sample Case Data
Rich realistic corporate files reflecting UK Companies House, KVK Netherlands,
ACRA Singapore filings, sanctions fuzzy hits, and 14-year on-premise archives.
"""

SAMPLE_CASES = {
    "NCB-CASE-7891": {
        "case_id": "NCB-CASE-7891",
        "client_name": "Apex Meridian Shipping Ltd",
        "entity_type": "Private Limited Company (UK)",
        "incorporation_country": "United Kingdom (Companies House #08941235)",
        "relationship_manager": "Mark Vance (Coverage)",
        "assigned_analyst": "Elena Gomez (KYC Ops)",
        "signed_mandate_date": "2026-10-15",
        "target_go_live_date": "2026-11-15",
        "days_in_progress": 32,
        "current_status": "Step 3: CDD File Build (Stalled waiting for 2nd outreach)",
        "source_filings": [
            {
                "doc_name": "UK_Companies_House_PSC_Register.pdf",
                "doc_id": "DOC-UK-01",
                "text": """COMPANIES HOUSE PSC REGISTER: APEX MERIDIAN SHIPPING LTD
Company Number: 08941235. Registered Office: 25 Bank Street, London, E14 5JP.
Share Capital: 100,000 Ordinary Shares of £1.00 each.
Shareholders:
- Meridian Holdings BV (Netherlands KVK: 74219902): 100,000 shares (100.0% voting rights).
Directors:
- Captain Robert Sterling (DOB: May 1968, British). Appointed: 12 Jan 2018."""
            },
            {
                "doc_name": "KVK_Netherlands_Extract_Meridian_BV.pdf",
                "doc_id": "DOC-NL-02",
                "text": """NETHERLANDS CHAMBER OF COMMERCE (KVK) EXTRACT
Dossier Number: 74219902. Legal Entity: Meridian Holdings B.V., Amsterdam.
Shareholding Structure:
- Pacific Crest Oceanic Pte Ltd (Singapore ACRA: 201829104K): 65,000 shares (65.0%).
- Sterling Maritime Trust (Guernsey Reg: GT-4410): 35,000 shares (35.0%)."""
            },
            {
                "doc_name": "ACRA_Singapore_Profile_PacificCrest.pdf",
                "doc_id": "DOC-SG-03",
                "text": """ACRA SINGAPORE BIZFILE CORPORATE PROFILE
Entity: Pacific Crest Oceanic Pte Ltd (UEN: 201829104K).
Shareholders:
- Chen Wei-Ming (Passport: E4819201A, Singaporean): 60.0% ordinary equity.
- Alistair Finch (Passport: G9921044B, British): 40.0% ordinary equity.
Ultimate Economic Entitlement:
Chen Wei-Ming holds 60% of 65% = 39.0% effective control.
Alistair Finch holds 40% of 65% = 26.0% effective control."""
            },
            {
                "doc_name": "Articles_of_Association_ApexMeridian.pdf",
                "doc_id": "DOC-ART-04",
                "text": """ARTICLES OF ASSOCIATION: APEX MERIDIAN SHIPPING LTD
Clause 4.2: No director may borrow funds exceeding £5,000,000 without written shareholder resolution from Meridian Holdings BV.
Clause 7.1: Certified Certificate of Incumbency required for any offshore corporate shareholder owning >20% within 12 months of mandate."""
            },
            {
                "doc_name": "Northgate_14Yr_Archive_Search_LondonFS02.txt",
                "doc_id": "DOC-ARCH-05",
                "text": """NORTHGATE ARCHIVE \\\\london-fs02\\kyc-historic\\meridian-group-2019\\
Folder ID: ARC-2019-MERIDIAN-01. Date: 14 June 2019.
Contains:
- Passport certified copy: Captain Robert Sterling (Valid until Nov 2028).
- Proof of Address: Sterling Maritime Trust deed extract (Recorded by MLRO in 2019).
NOTE: Alistair Finch passport copy NOT found in historic repository."""
            }
        ],
        "raw_screening_hits": [
            {
                "hit_id": "SCR-7891-01",
                "target_name": "Robert Sterling",
                "hit_category": "PEP (Politically Exposed Person)",
                "matched_record": "Robert Charles Sterling (Former Member of Parliament, New Zealand, born 1944)",
                "confidence_score": 0.88,
                "notes": "Fuzzy match on 'Robert Sterling'. Northgate client Captain Robert Sterling born May 1968 in UK."
            },
            {
                "hit_id": "SCR-7891-02",
                "target_name": "Meridian Holdings",
                "hit_category": "Sanctions / OFAC",
                "matched_record": "Meridian Maritime LLC (Crimea / Sevastopol Sanctioned Entity)",
                "confidence_score": 0.81,
                "notes": "Fuzzy name similarity. Target is Dutch B.V. incorporated in Amsterdam, zero links to Crimea."
            }
        ]
    },
    "NCB-CASE-8402": {
        "case_id": "NCB-CASE-8402",
        "client_name": "Vanguard Energy Infrastructure PLC",
        "entity_type": "Public Limited Company (UK)",
        "incorporation_country": "United Kingdom (LSE Listed)",
        "relationship_manager": "Mark Vance (Coverage)",
        "assigned_analyst": "Elena Gomez (KYC Ops)",
        "signed_mandate_date": "2026-10-22",
        "target_go_live_date": "2026-11-20",
        "days_in_progress": 25,
        "current_status": "Step 3: CDD File Build",
        "source_filings": [
            {
                "doc_name": "LSE_Regulatory_Filing_Vanguard.pdf",
                "doc_id": "DOC-LSE-01",
                "text": """LONDON STOCK EXCHANGE DISCLOSURE: VANGUARD ENERGY INFRASTRUCTURE PLC
Major Shareholdings (>3%):
- Global Transition Infrastructure Fund (Cayman LP): 28.5%
- UK Institutional Pension Pool: 14.2%
- Free float (Institutional & Retail): 57.3%
Chairman & CEO: Sir Marcus Thornton."""
            }
        ],
        "raw_screening_hits": []
    }
}
