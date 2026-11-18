"""
Northgate Enterprise Agent - Base Agent Class
Provides standardized agent metadata, ownership attribution, tracing, and metric collection.
"""
import time
import uuid
from typing import Dict, Any, Optional
from ..governance import governance, ActionAuditRecord
from ..model_gateway import model_gateway, ModelResponse
from ..auth import AuthUser

class BaseEnterpriseAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        # Fetch current config from governance registry
        self.config = governance.agent_configs[agent_id]

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def owner(self) -> str:
        return self.config.owner

    @property
    def version(self) -> str:
        return self.config.version

    def execute_with_governance(
        self,
        case_id: str,
        user: AuthUser,
        prompt: str,
        system_instruction: str,
        mock_generator: Any,
        input_summary: str = "",
        citations_count: int = 0
    ) -> Dict[str, Any]:
        """
        Executes model call with full governance tracking, fallback safety,
        and agent owner transparency.
        """
        trace_id = str(uuid.uuid4())
        action_id = f"ACT-{uuid.uuid4().hex[:8].upper()}"
        start_time = time.time()

        # Execute through Model Gateway (handles Primary -> Fallback)
        response: ModelResponse = model_gateway.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            primary_model=self.config.assigned_primary_model,
            fallback_model=self.config.assigned_fallback_model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_output_tokens,
            mock_response_generator=mock_generator
        )

        latency = int((time.time() - start_time) * 1000)

        # Build Audit Record
        audit_record = ActionAuditRecord(
            trace_id=trace_id,
            action_id=action_id,
            case_id=case_id,
            agent_id=self.agent_id,
            agent_name=self.name,
            agent_owner=self.owner,
            agent_version=self.version,
            requested_by_user=user.full_name,
            requested_by_role=user.role,
            model_requested=self.config.assigned_primary_model,
            model_actual=response.model_name,
            provider_actual=response.provider,
            is_fallback=response.is_fallback,
            fallback_reason=response.fallback_reason,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            total_tokens=response.total_tokens,
            cost_usd=response.cost_usd,
            latency_ms=latency,
            status="FALLBACK_TRIGGERED" if response.is_fallback else "SUCCESS",
            citations_count=citations_count,
            human_signoff_required=True,
            human_signoff_status="PENDING",
            input_summary=input_summary,
            output_summary=response.content[:180] + "..." if len(response.content) > 180 else response.content
        )

        governance.record_action(audit_record)

        return {
            "trace_id": trace_id,
            "action_id": action_id,
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "agent_owner": self.owner,
            "agent_version": self.version,
            "model_used": response.model_name,
            "provider": response.provider,
            "is_fallback": response.is_fallback,
            "fallback_reason": response.fallback_reason,
            "cost_usd": response.cost_usd,
            "latency_ms": latency,
            "tokens": {
                "input": response.input_tokens,
                "output": response.output_tokens,
                "total": response.total_tokens
            },
            "content": response.content
        }
