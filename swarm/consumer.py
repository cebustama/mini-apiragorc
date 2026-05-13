import os
import time
from kafka import KafkaConsumer
import json
from swarm.orchestrator import SwarmOrchestrator
from audit.auditor import audit

bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

consumer = None
while consumer is None:
    try:
        consumer = KafkaConsumer(
            "incidents",
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode("utf-8"))
        )
        print("✅ Conectado a Kafka")
    except Exception:
        print("⏳ Kafka no disponible, reintentando en 5s...")
        time.sleep(5)

swarm = SwarmOrchestrator()

print("✅ SWARM consumer escuchando eventos en Kafka…")

for message in consumer:
    event = message.value
    incident = event.get("incident")

    audit("INCIDENT_RECEIVED", incident)
    audit("ORCHESTRATION_START", {"incident_id": incident["id"]})

    result = swarm.execute(incident)

    audit("SWARM_RESULT", result)

    print("🧠 Resultado del SWARM:")
    for agent, output in result.items():
        print(f" - {agent}: {output}")
