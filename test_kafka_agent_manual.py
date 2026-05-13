# test_kafka_agent_manual.py

from dotenv import load_dotenv
load_dotenv()

from swarm.llm.bedrock_client import BedrockLLMClient
from swarm.agents.kafka_diagnosis_agent import KafkaDiagnosisAgent

# 1. Construir el cliente LLM (Bedrock)
llm_client = BedrockLLMClient()

# 2. Construir el agente
agent = KafkaDiagnosisAgent(llm_client)

# 3. Contexto de prueba (incidencia Kafka simulada)
context = {
    "incident": {
        "error": "Consumer lag increasing rapidly",
        "topic": "orders",
        "consumer_group": "billing",
        "lag": 45000,
        "brokers_status": {
            "broker-1": "up",
            "broker-2": "down"
        }
    }
}

# 4. Ejecutar el agente
result = agent.execute(context)

# 5. Mostrar resultado
print("\n=== Diagnosis Result ===")
print(result)
