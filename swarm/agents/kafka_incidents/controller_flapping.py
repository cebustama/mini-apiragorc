from swarm.agents.schemas import KafkaIncident

CONTROLLER_FLAPPING = KafkaIncident(
    cluster="dev-cluster",
    error="Controller instability",
    symptoms="Kafka controller keeps changing frequently",
    logs=[
        "New controller elected: broker 1",
        "Controller moved from broker 1 to broker 3",
        "Controller moved from broker 3 to broker 2"
    ],
    metrics={
        "controller_changes_last_minute": 5
    }
)