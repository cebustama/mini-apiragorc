import json
import logging

from swarm.agents import BaseAgent
from swarm.agents.schemas import KafkaIncident, DiagnosisResult
from swarm.llm.client import LLMClient

logger = logging.getLogger(__name__)


class KafkaDiagnosisAgent(BaseAgent):
    """
    Cognitive agent responsible for diagnosing Kafka incidents using an LLM.

    Key properties:
    - Receives a context dict (never raw models directly in production)
    - Applies deterministic policy before invoking the LLM
    - Uses the LLM strictly as an analytical tool
    - Enforces schema validation and fail-closed behavior
    - Provides full observability via structured logging
    """

    name = "KafkaDiagnosisAgent"
    type = "cognitive"

    inputs = ["incident"]
    outputs = ["diagnosis"]

    PROMPT_TEMPLATE = """You are a Kafka operations expert.

Given the following Kafka incident, identify the most probable root causes.

Return ONLY valid JSON matching exactly this schema:
{{
  "causes": [
    {{
      "code": "STRING",
      "description": "STRING",
      "confidence": 0.0
    }}
  ]
}}

Rules:
- Max 5 causes
- Confidence between 0 and 1
- Sorted by confidence descending
- No extra text outside JSON
- If uncertain, return an empty causes list

Incident:
{incident_json}
"""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def execute(self, context: dict) -> DiagnosisResult:
        logger.info("KafkaDiagnosisAgent: execution started")

        # ---------- 1. Extract and validate incident ----------
        try:
            incident = KafkaIncident.model_validate(context["incident"])
        except Exception as exc:
            logger.warning("KafkaDiagnosisAgent: invalid incident in context")
            logger.warning(str(exc))
            return DiagnosisResult(causes=[])

        logger.info(
            "KafkaDiagnosisAgent: incident received (error=%s)",
            incident.error,
        )

        # ---------- 2. Deterministic policy (exploration mode) ----------
        if not self._should_use_llm(incident):
            logger.info(
                "KafkaDiagnosisAgent: LLM invocation skipped by policy"
            )
            return DiagnosisResult(causes=[])

        # ---------- 3. Build prompt ----------
        incident_json = incident.model_dump_json(indent=2)
        prompt = self.PROMPT_TEMPLATE.format(
            incident_json=incident_json
        )

        logger.info("KafkaDiagnosisAgent: invoking LLM")

        # ---------- 4. Invoke LLM ----------
        raw_output = self.llm_client.invoke(prompt)

        if not raw_output:
            logger.info(
                "KafkaDiagnosisAgent: empty LLM output (fail-closed)"
            )
            return DiagnosisResult(causes=[])

        # ---------- 5. Normalize and parse LLM output ----------
        cleaned_output = self._strip_code_fences(raw_output)

        try:
            data = json.loads(cleaned_output)
            result = DiagnosisResult.model_validate(data)

            logger.info(
                "KafkaDiagnosisAgent: diagnosis produced with %d causes",
                len(result.causes),
            )
            return result

        except Exception as exc:
            logger.warning(
                "KafkaDiagnosisAgent: LLM output discarded by schema"
            )
            logger.warning(str(exc))
            return DiagnosisResult(causes=[])

    def _should_use_llm(self, incident: KafkaIncident) -> bool:
        """
        Exploration-mode policy.

        For now, invoke the LLM whenever an error is present.
        This will be tightened again once prompt and schema behavior
        are fully characterized.
        """
        return bool(getattr(incident, "error", None))

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        """
        Remove Markdown code fences (``` or ```json) if present.

        This normalizes common LLM formatting without weakening
        schema validation or fail-closed guarantees.
        """
        text = text.strip()

        if text.startswith("```"):
            lines = text.splitlines()
            lines = [
                line for line in lines
                if not line.strip().startswith("```")
            ]
            text = "\n".join(lines)

        return text.strip()