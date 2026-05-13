from swarm.agents.schemas import KafkaIncident

BROKER_DOWN = KafkaIncident(
    cluster="dev-cluster",
    error="Broker unreachable",
    symptoms="Producers and consumers experience intermittent connection failures",
    logs=[
        "Connection to node 2 (/10.0.0.12:9092) failed",
        "Retrying connection to node 2",
        "Broker 2 disconnected"
    ],
    metrics={
        "offline_partitions": 8,
        "under_replicated_partitions": 8
    }
)