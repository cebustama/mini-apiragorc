from swarm.agents.schemas import KafkaIncident

PRODUCER_TIMEOUT = KafkaIncident(
    cluster="dev-cluster",
    error="Producer request timeout",
    symptoms="Kafka producers fail with request timeouts",
    logs=[
        "Expiring 1 record(s) due to timeout",
        "Error sending record to topic payments"
    ],
    metrics={
        "request_timeout_ms": 30000,
        "in_flight_requests": 5
    }
)