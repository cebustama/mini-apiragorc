from swarm.agents.schemas import KafkaIncident

UNDER_REPLICATED_PARTITIONS = KafkaIncident(
    cluster="dev-cluster",
    error="Under-replicated partitions detected",
    symptoms="Cluster reports under-replicated partitions for a prolonged period",
    logs=[
        "Under replicated partitions detected",
        "Replica fetcher lag increasing on broker 1"
    ],
    metrics={
        "under_replicated_partitions": 15,
        "replication_factor": 3
    }
)