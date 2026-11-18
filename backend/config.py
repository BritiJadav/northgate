"""
Northgate Enterprise Agent - Configuration
Enterprise-grade settings for Security, Model Providers, Governance, and Fallbacks.
"""
import os
from pydantic import BaseModel
from typing import Dict, Optional

class ModelPricing(BaseModel):
    input_cost_per_million: float
    output_cost_per_million: float

class AppConfig:
    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")

    # User Credentials with Passwords for Form-Based Authentication
    USER_CREDENTIALS: Dict[str, Dict] = {
        "elena.gomez": {
            "password": "Analyst@2026!",
            "token": "token-elena-analyst",
            "api_key": "northgate-analyst-key-101",
            "role": "analyst",
            "full_name": "Elena Gomez",
            "department": "KYC Operations London"
        },
        "sarah.jenkins": {
            "password": "OpsLead@2026!",
            "token": "token-sarah-ops",
            "api_key": "northgate-ops-key-202",
            "role": "ops_lead",
            "full_name": "Sarah Jenkins",
            "department": "Head of KYC Operations"
        },
        "david.ross": {
            "password": "MLRO@2026!",
            "token": "token-david-mlro",
            "api_key": "northgate-mlro-key-303",
            "role": "mlro",
            "full_name": "David Ross",
            "department": "Compliance & MLRO Office"
        },
        "priya.sharma": {
            "password": "Admin@2026!",
            "token": "token-priya-admin",
            "api_key": "northgate-admin-key-999",
            "role": "admin",
            "full_name": "Priya Sharma",
            "department": "Enterprise Architecture"
        }
    }

    # Security: Valid API Keys and Mock Auth Tokens for RBAC
    API_KEYS: Dict[str, Dict] = {
        "northgate-analyst-key-101": {
            "client_name": "KYC Workbench UI (Analyst)",
            "roles": ["analyst"],
            "owner": "Elena Gomez"
        },
        "northgate-ops-key-202": {
            "client_name": "KYC Ops Management Portal",
            "roles": ["ops_lead", "analyst"],
            "owner": "Sarah Jenkins"
        },
        "northgate-mlro-key-303": {
            "client_name": "MLRO Governance Console",
            "roles": ["mlro", "analyst"],
            "owner": "David Ross"
        },
        "northgate-admin-key-999": {
            "client_name": "Enterprise Architecture & Gateway Admin",
            "roles": ["admin", "ops_lead", "mlro", "analyst"],
            "owner": "Priya Sharma"
        }
    }

    # Bearer Tokens (JWT / Session Mock)
    AUTH_TOKENS: Dict[str, Dict] = {
        "token-elena-analyst": {
            "user_id": "usr-elena-01",
            "username": "elena.gomez",
            "full_name": "Elena Gomez",
            "role": "analyst",
            "department": "KYC Operations London"
        },
        "token-sarah-ops": {
            "user_id": "usr-sarah-02",
            "username": "sarah.jenkins",
            "full_name": "Sarah Jenkins",
            "role": "ops_lead",
            "department": "Head of KYC Operations"
        },
        "token-david-mlro": {
            "user_id": "usr-david-03",
            "username": "david.ross",
            "full_name": "David Ross",
            "role": "mlro",
            "department": "Compliance & Anti-Money Laundering"
        },
        "token-priya-admin": {
            "user_id": "usr-priya-04",
            "username": "priya.sharma",
            "full_name": "Priya Sharma",
            "role": "admin",
            "department": "Enterprise Architecture"
        }
    }

    # GCP Project & Region (Lab Usage Guidelines: asia-south1)
    GCP_PROJECT: str = os.getenv("GCP_PROJECT", "slabspro-slabsuser41")
    GCP_REGION: str = os.getenv("GCP_REGION", "asia-south1")

    # Model Pricing Matrix (per 1,000,000 tokens in USD)
    # Approved Lab Models: Gemini 3 Flash Preview & gemini-embedding-001
    PRICING_TABLE: Dict[str, ModelPricing] = {
        "gemini-3-flash-preview": ModelPricing(input_cost_per_million=0.50, output_cost_per_million=1.50),
        "gemini-1.5-pro": ModelPricing(input_cost_per_million=3.50, output_cost_per_million=10.50),
        "gemini-1.5-flash": ModelPricing(input_cost_per_million=0.35, output_cost_per_million=1.05),
        "claude-3-5-sonnet": ModelPricing(input_cost_per_million=3.00, output_cost_per_million=15.00),
        "gpt-4o": ModelPricing(input_cost_per_million=2.50, output_cost_per_million=10.00),
        "enterprise-local-llama3": ModelPricing(input_cost_per_million=0.20, output_cost_per_million=0.20),
    }

    # External Provider Keys (Read from environment if provided)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    SECONDARY_API_KEY: Optional[str] = os.getenv("SECONDARY_API_KEY")

config = AppConfig()
