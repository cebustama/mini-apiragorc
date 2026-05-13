import json

from .schemas import PlannerInput, PlannerOutput
from .prompts import PLANNER_SYSTEM_PROMPT
from .kafka_rules import plan_kafka_incident


class LLMPlanner:
    """
    Hybrid planner:
    - Rules-first (deterministic)
    - LLM-backed fallback
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def plan(
        self,
        event: dict,
        state: dict,
        agents: list,
        policies: dict,
    ) -> PlannerOutput:
        # --- 1. Deterministic Kafka rule ---
        kafka_plan = plan_kafka_incident(event)
        if kafka_plan is not None:
            return kafka_plan

        # --- 2. Fallback to LLM planner ---
        if self.llm_client is None:
            return self._empty_plan()

        planner_input = PlannerInput(
            event=event,
            state=state,
            available_agents=agents,
            policies=policies,
        )

        raw_response = self._call_llm(planner_input)
        return self._parse_and_validate(raw_response, policies)

    def _call_llm(self, planner_input: PlannerInput) -> str:
        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": planner_input.model_dump_json(),
            },
        ]
        return self.llm_client.chat(messages)

    def _parse_and_validate(
        self,
        raw_response: str,
        policies: dict,
    ) -> PlannerOutput:
        try:
            parsed = json.loads(raw_response)
            plan = PlannerOutput(**parsed)

            # ---- Policy validation: max_steps ----
            max_steps = policies.get("max_steps")
            if max_steps is not None and len(plan.plan) > max_steps:
                return self._empty_plan()

            return plan

        except Exception:
            # Hard failure → empty, safe plan
            return self._empty_plan()

    def _empty_plan(self) -> PlannerOutput:
        return PlannerOutput(
            intent="none",
            confidence=0.0,
            plan=[],
        )