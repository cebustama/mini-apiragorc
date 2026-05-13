class ExecutionError(Exception):
    pass


class PlanExecutor:
    def __init__(self, agent_registry: dict, max_retries: int = 2):
        self.agent_registry = agent_registry
        self.max_retries = max_retries

    def execute(self, plan, context: dict):
        for step in sorted(plan.plan, key=lambda s: s.step):
            agent = self.agent_registry.get(step.agent)

            if agent is None:
                raise ExecutionError(f"Agent not found: {step.agent}")

            try:
                self._execute_step(agent, step, context)

            except Exception as exc:
                should_continue = self._handle_failure(
                    agent=agent,
                    step=step,
                    context=context,
                    exception=exc
                )

                if not should_continue:
                    break

    # -----------------------------

    def _execute_step(self, agent, step, context: dict):
        agent.execute(context)

    # -----------------------------

    def _handle_failure(self, agent, step, context: dict, exception: Exception) -> bool:
        policy = step.failure_policy

        if policy == "abort":
            return False

        if policy == "continue":
            return True

        if policy == "retry":
            for _ in range(self.max_retries):
                try:
                    self._execute_step(agent, step, context)
                    return True
                except Exception:
                    continue
            return False

        raise ExecutionError(f"Unknown failure_policy: {policy}")
