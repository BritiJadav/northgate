"""
Northgate Enterprise Agent Gateway - Launcher Script
Starts FastAPI backend server serving both REST API and Interactive UI.
"""
import uvicorn
from backend.config import config

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 STARTING NORTHGATE ENTERPRISE AGENT GATEWAY")
    print("=" * 70)
    print(f"👉 API & Backend Docs: http://{config.HOST}:{config.PORT}/docs")
    print(f"👉 Interactive Frontend UI: http://{config.HOST}:{config.PORT}/static/index.html")
    print("=" * 70)
    print("Architecture Pillars:")
    print("  [A] Security: API-based Auth & RBAC (Bearer & X-API-Key Headers)")
    print("  [B] Agent Toner: Decoupled Dynamic Model Registry & Swapping")
    print("  [C] Governance: Per-Action Cost Tracing & Agent Owner Transparency")
    print("  [D] Resilience: Primary -> Secondary Multi-Provider Auto-Failover")
    print("  [E] Critic: Second-Line Hallucination & Citation Verification")
    print("=" * 70)
    uvicorn.run("backend.app:app", host=config.HOST, port=config.PORT, reload=False)
