import pytest
from swarm.executor import PlanExecutor, ExecutionError
from swarm.planner.schemas import PlannerOutput, ExecutionStep

class SuccessAgent:
    type = "deterministic"
    inputs = []
    outputs = []

    def execute(self, context):
        context["executed"] = context.get("executed", 0) + 1

class FailingAgent:
    type = "deterministic"
    inputs = []
    outputs = []

    def execute(self, context):
        raise RuntimeError("boom")
    
class FlakyAgent:
    def __init__(self):
        self.calls = 0

    type = "deterministic"
    inputs = []
    outputs = []

    def execute(self, context):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("temporary failure")
        context["executed"] = True

def test_executor_abort_on_failure():
    agent_registry = {
        "GoodAgent": SuccessAgent(),
        "BadAgent": FailingAgent(),
    }

    executor = PlanExecutor(agent_registry)

    plan = PlannerOutput(
        intent="test",
        confidence=1.0,
        plan=[
            ExecutionStep(
                step=1,
                agent="BadAgent",
                input_map=[],
                failure_policy="abort"
            ),
            ExecutionStep(
                step=2,
                agent="GoodAgent",
                input_map=[],
                failure_policy="continue"
            ),
        ]
    )

    context = {}

    executor.execute(plan, context)

    # GoodAgent NO debe ejecutarse
    assert "executed" not in context

def test_executor_continue_on_failure():
    agent_registry = {
        "BadAgent": FailingAgent(),
        "GoodAgent": SuccessAgent(),
    }

    executor = PlanExecutor(agent_registry)

    plan = PlannerOutput(
        intent="test",
        confidence=1.0,
        plan=[
            ExecutionStep(
                step=1,
                agent="BadAgent",
                input_map=[],
                failure_policy="continue"
            ),
            ExecutionStep(
                step=2,
                agent="GoodAgent",
                input_map=[],
                failure_policy="abort"
            ),
        ]
    )

    context = {}

    executor.execute(plan, context)

    # GoodAgent SÍ debe ejecutarse
    assert context["executed"] == 1

def test_executor_retry_success():
    flaky_agent = FlakyAgent()

    agent_registry = {
        "FlakyAgent": flaky_agent,
    }

    executor = PlanExecutor(agent_registry, max_retries=2)

    plan = PlannerOutput(
        intent="test",
        confidence=1.0,
        plan=[
            ExecutionStep(
                step=1,
                agent="FlakyAgent",
                input_map=[],
                failure_policy="retry"
            ),
        ]
    )

    context = {}

    executor.execute(plan, context)

    assert context["executed"] is True
    assert flaky_agent.calls == 2

def test_executor_retry_exhausted():
    agent_registry = {
        "BadAgent": FailingAgent(),
    }

    executor = PlanExecutor(agent_registry, max_retries=2)

    plan = PlannerOutput(
        intent="test",
        confidence=1.0,
        plan=[
            ExecutionStep(
                step=1,
                agent="BadAgent",
                input_map=[],
                failure_policy="retry"
            ),
        ]
    )

    context = {}

    executor.execute(plan, context)

    # Nunca se ejecuta con éxito
    assert context == {}

def test_executor_unknown_agent():
    executor = PlanExecutor(agent_registry={})

    plan = PlannerOutput(
        intent="test",
        confidence=1.0,
        plan=[
            ExecutionStep(
                step=1,
                agent="GhostAgent",
                input_map=[],
                failure_policy="abort"
            ),
        ]
    )

    with pytest.raises(ExecutionError):
        executor.execute(plan, {})