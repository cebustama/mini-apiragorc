import os
import time
import json
from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer

app = FastAPI()

# --- Configuración Kafka ---
bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

producer = None

while producer is None:
    try:
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        print("✅ API conectada a Kafka")
    except Exception as e:
        print("⏳ Kafka no disponible, reintentando en 5s...")
        time.sleep(5)

# --- Modelo ---
class Incident(BaseModel):
    id: str
    description: str

# --- Endpoint ---
@app.post("/incident")
def create_incident(incident: Incident):
    event = {
        "type": "INCIDENT_CREATED",
        "incident": incident.dict()
    }

    producer.send("incidents", event)
    producer.flush()

    return {
        "status": "accepted",
        "incident_id": incident.id
    }