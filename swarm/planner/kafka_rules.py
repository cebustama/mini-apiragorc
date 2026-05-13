from swarm.planner.schemas import ExecutionStep, PlannerOutput


def plan_kafka_incident(event: dict) -> PlannerOutput | None:
    if event.get("system") != "kafka":
        return None

    return PlannerOutput(
        intent="diagnose_kafka_incident",
        confidence=0.9,
        plan=[
            ExecutionStep(
                step=1,
                agent="KafkaDiagnosisAgent",
                input_map=["incident"],
                failure_policy="continue",
            )
        ],
    )