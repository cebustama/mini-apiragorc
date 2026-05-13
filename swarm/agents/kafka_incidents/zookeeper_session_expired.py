from swarm.agents.schemas import KafkaIncident

ZOOKEEPER_SESSION_EXPIRED = KafkaIncident(
    cluster="dev-cluster",
    error="ZooKeeper session expired",
    symptoms="Kafka brokers disconnected from ZooKeeper",
    logs=[
        "ZooKeeper session expired",
        "Lost connection to ZooKeeper"
    ],
    metrics={
        "zookeeper_disconnects": 3
    }
)