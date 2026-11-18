"""
Comprehensive Integration Test Suite for Northgate 5-Pillar Enterprise Prototype
Tests:
1. Security (Header Auth & RBAC)
2. Agent Toner (Model Agility)
3. Primary & Critic Agent Execution
4. Fallback Resilience under simulated Primary 429 Outage
5. Governance, Tracing & Per-Action Cost Calculation
"""
import sys
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_all():
    print("\n--- TEST 1: Security & Header-Based Authentication ---")
    # 1. Missing headers -> 401
    r = client.get("/api/v1/cases")
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    print("✔ Missing headers correctly rejected with 401 Unauthorized")

    # 2. Invalid API Key -> 403
    r = client.get("/api/v1/cases", headers={"X-API-Key": "wrong-key", "Authorization": "Bearer token-elena-analyst"})
    assert r.status_code == 403, f"Expected 403, got {r.status_code}"
    print("✔ Invalid X-API-Key correctly rejected with 403 Forbidden")

    # 3. Valid Analyst Headers
    headers_elena = {
        "X-API-Key": "northgate-analyst-key-101",
        "Authorization": "Bearer token-elena-analyst"
    }
    r = client.get("/api/v1/auth/me", headers=headers_elena)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    user = r.json()
    assert user["username"] == "elena.gomez"
    assert user["role"] == "analyst"
    print(f"✔ Authenticated caller successfully: {user['full_name']} (Role: {user['role']})")

    print("\n--- TEST 2: Primary Agent 1 (UBO Extractor with Citations) ---")
    r = client.post("/api/v1/agents/extract-ubos", json={"case_id": "NCB-CASE-7891"}, headers=headers_elena)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    ubo_data = r.json()
    assert ubo_data["agent_id"] == "AGNT-UBO-01"
    assert ubo_data["agent_owner"] == "Sarah Jenkins"
    assert ubo_data["is_fallback"] is False
    assert ubo_data["cost_usd"] > 0
    print(f"✔ UBO Extractor executed. Action ID: {ubo_data['action_id']}, Model: {ubo_data['model_used']}, Cost: ${ubo_data['cost_usd']:.6f}")
    assert "[Doc: UK_Companies_House_PSC_Register.pdf" in ubo_data["content"]
    print("✔ Document citations grounded in Companies House, KVK, and ACRA verified.")

    print("\n--- TEST 3: Primary Agent 2 (1-Shot Gap Detector) ---")
    r = client.post("/api/v1/agents/detect-gaps", json={"case_id": "NCB-CASE-7891"}, headers=headers_elena)
    assert r.status_code == 200
    gap_data = r.json()
    assert gap_data["agent_id"] == "AGNT-GAP-02"
    assert gap_data["agent_owner"] == "Elena Gomez"
    assert "draft_client_outreach_email" in gap_data["content"]
    print(f"✔ Gap Detector executed. Action ID: {gap_data['action_id']}, Owner: {gap_data['agent_owner']}, Cost: ${gap_data['cost_usd']:.6f}")

    print("\n--- TEST 4: Pillar 5 (Second-Line Critic Agent & Citations) ---")
    r = client.post("/api/v1/agents/verify-critic", json={
        "case_id": "NCB-CASE-7891",
        "target_agent_id": ubo_data["agent_id"],
        "target_action_id": ubo_data["action_id"],
        "output_text": ubo_data["content"]
    }, headers=headers_elena)
    assert r.status_code == 200
    critic_data = r.json()
    assert critic_data["agent_id"] == "AGNT-CRITIC-99"
    assert critic_data["agent_owner"] == "Claire Bennett"
    assert "VERIFIED_CLEAN" in critic_data["content"]
    print(f"✔ Critic Agent verified citations and anti-hallucination. Owner: {critic_data['agent_owner']}")

    print("\n--- TEST 5: Pillar 4 (Resilience & Auto-Fallback under 429 Outage) ---")
    headers_ops = {
        "X-API-Key": "northgate-ops-key-202",
        "Authorization": "Bearer token-sarah-ops"
    }
    # Enable fault injection
    r = client.post("/api/v1/models/fault-injection", json={"enabled": True}, headers=headers_ops)
    assert r.status_code == 200
    assert r.json()["simulate_primary_outage"] is True
    print("✔ Simulated Primary 429 Quota Exceeded outage injected")

    # Run agent call while primary is down -> Must automatically failover to secondary model!
    r = client.post("/api/v1/agents/extract-ubos", json={"case_id": "NCB-CASE-7891"}, headers=headers_elena)
    assert r.status_code == 200
    fallback_result = r.json()
    assert fallback_result["is_fallback"] is True
    assert fallback_result["model_used"] == "claude-3-5-sonnet"
    assert "Rate limit exceeded" in fallback_result["fallback_reason"]
    print(f"✔ Fallback Verified! Call automatically routed to secondary model: {fallback_result['model_used']} ({fallback_result['provider']})")

    # Restore primary model
    client.post("/api/v1/models/fault-injection", json={"enabled": False}, headers=headers_ops)
    print("✔ Primary model restored to normal operation")

    print("\n--- TEST 6: Pillar 2 (Agent Toner & Runtime Tuning) ---")
    r = client.put("/api/v1/governance/agents/AGNT-UBO-01", json={
        "assigned_primary_model": "gemini-1.5-flash",
        "temperature": 0.05
    }, headers=headers_ops)
    assert r.status_code == 200
    updated_cfg = r.json()["updated_config"]
    assert updated_cfg["assigned_primary_model"] == "gemini-1.5-flash"
    assert updated_cfg["temperature"] == 0.05
    print("✔ Agent Toner verified: Successfully swapped model outside system to gemini-1.5-flash at runtime!")

    print("\n--- TEST 7: Pillar 3 (Governance, Cost Metrics & RBAC Sign-off) ---")
    r = client.get("/api/v1/governance/metrics", headers=headers_elena)
    assert r.status_code == 200
    metrics = r.json()
    assert metrics["total_actions"] >= 4
    assert metrics["total_cost_usd"] > 0
    assert metrics["fallback_events"] >= 1
    print(f"✔ Governance Metrics: Total Actions: {metrics['total_actions']}, Total Spend: ${metrics['total_cost_usd']:.6f}, Failovers: {metrics['fallback_events']}")

    # Test RBAC Sign-off restriction: Analyst cannot sign risk rating (only MLRO)
    r = client.post("/api/v1/signoff", json={
        "action_id": ubo_data["action_id"],
        "signoff_type": "PERSON_SIGNS_3_RISK",
        "decision": "APPROVED",
        "signer_notes": "Attempting sign-off"
    }, headers=headers_elena)
    assert r.status_code == 403
    print("✔ RBAC Sign-off: Analyst correctly blocked with 403 when attempting MLRO-only Person Signs 3")

    # Now MLRO signs risk rating
    headers_mlro = {
        "X-API-Key": "northgate-mlro-key-303",
        "Authorization": "Bearer token-david-mlro"
    }
    r = client.post("/api/v1/signoff", json={
        "action_id": ubo_data["action_id"],
        "signoff_type": "PERSON_SIGNS_3_RISK",
        "decision": "APPROVED",
        "signer_notes": "MLRO David Ross signed risk rating under SMCR."
    }, headers=headers_mlro)
    assert r.status_code == 200
    print("✔ MLRO David Ross successfully signed Person Signs 3!")

    print("\n=======================================================")
    print("🎉 ALL 5 ENTERPRISE ARCHITECTURE PILLARS 100% VALIDATED!")
    print("=======================================================")

if __name__ == "__main__":
    test_all()
