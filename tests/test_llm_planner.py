import pytest
from swarm.planner.llm_planner import LLMPlanner


# -----------------------
# Fixtures comunes
# -----------------------

@pytest.fixture
def base_event():
    return {
        "type": "incident_created",
        "payload": {
            "location": "Sevilla",
            "description": "Test incident"
        }
    }


@pytest.fixture
def agents():
    return [
        {
            "name": "GeoAgent",
            "type": "deterministic",
            "inputs": ["location"],
            "outputs": ["coordinates"]
        }
    ]


@pytest.fixture
def policies():
    return {
        "max_steps": 1
    }


# -----------------------
# Mocks de LLM
# -----------------------

class FakeLLM:
    """LLM que devuelve un plan válido"""
    def chat(self, messages):
        return """
        {
          "intent": "incident_resolution",
          "confidence": 0.9,
          "plan": [
            {
              "step": 1,
              "agent": "GeoAgent",
              "input_map": ["event.payload.location"],
              "failure_policy": "abort"
            }
          ]
        }
        """


class BrokenLLM:
    """LLM que devuelve basura (no JSON)"""
    def chat(self, messages):
        return "THIS IS NOT JSON 🤡"


class EmptyPlanLLM:
    """LLM que devuelve un plan vacío válido"""
    def chat(self, messages):
        return """
        {
          "intent": "none",
          "confidence": 0.0,
          "plan": []
        }
        """


class TooManyStepsLLM:
    """LLM que viola la policy max_steps"""
    def chat(self, messages):
        return """
        {
          "intent": "incident_resolution",
          "confidence": 0.9,
          "plan": [
            {
              "step": 1,
              "agent": "GeoAgent",
              "input_map": ["event.payload.location"],
              "failure_policy": "abort"
            },
            {
              "step": 2,
              "agent": "GeoAgent",
              "input_map": ["event.payload.location"],
              "failure_policy": "abort"
            }
          ]
        }
        """


# -----------------------
# Tests
# -----------------------

def test_planner_generates_valid_plan(base_event, agents, policies):
    planner = LLMPlanner(llm_client=FakeLLM())

    plan = planner.plan(
        event=base_event,
        state={},
        agents=agents,
        policies=policies
    )

    assert plan.confidence > 0
    assert len(plan.plan) == 1
    assert plan.plan[0].agent == "GeoAgent"


def test_planner_handles_invalid_llm_output(base_event, agents, policies):
    planner = LLMPlanner(llm_client=BrokenLLM())

    plan = planner.plan(
        event=base_event,
        state={},
        agents=agents,
        policies=policies
    )

    assert plan.confidence == 0.0
    assert plan.plan == []


def test_planner_accepts_empty_plan(base_event, agents, policies):
    planner = LLMPlanner(llm_client=EmptyPlanLLM())

    plan = planner.plan(
        event=base_event,
        state={},
        agents=agents,
        policies=policies
    )

    assert plan.confidence == 0.0
    assert plan.plan == []


def test_planner_rejects_plan_exceeding_max_steps(base_event, agents, policies):
    """
    Si el LLM devuelve más pasos que max_steps, el plan
    debe considerarse inválido y resultar en plan vacío.
    """
    planner = LLMPlanner(llm_client=TooManyStepsLLM())

    plan = planner.plan(
        event=base_event,
        state={},
        agents=agents,
        policies=policies
    )

    assert plan.confidence == 0.0
    assert plan.plan == []
