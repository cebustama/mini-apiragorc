from swarm.planner import LLMPlanner
from swarm.executor import PlanExecutor


class Orchestrator:
    def __init__(self, llm_client, agent_registry):
        self.planner = LLMPlanner(llm_client)
        self.executor = PlanExecutor(agent_registry)

    def handle_event(self, event):
        state = {"incident_progress": "new"}

        agents = [
            {
                "name": name,
                "type": agent.type,
                "inputs": agent.inputs,
                "outputs": agent.outputs,
            }
            for name, agent in self.executor.agent_registry.items()
        ]

        policies = {
            "max_steps": 5
        }

        plan = self.planner.plan(event, state, agents, policies)

        if plan.plan and plan.confidence >= 0.6:
            self.executor.execute(plan, event)