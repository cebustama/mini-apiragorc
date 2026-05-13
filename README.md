# MINI‑APIRAGORC

Mini‑APIRAGORC is a minimal, production‑oriented reference architecture for
LLM‑assisted, event‑driven agent systems.

The system is designed around strict separation of responsibilities:
- Planners decide *what* to do
- Executors decide *how* to run it
- Agents execute or fail
- LLMs are governed by schemas and policies

---

## Architecture Overview

Client → FastAPI → Kafka → SWARM Consumer → Planner → Executor → Agents

Key properties:
- Event‑driven (Kafka backbone)
- Fire‑and‑forget API
- Deterministic planner (fail‑closed)
- Isolated, testable agents
- Infrastructure‑independent unit tests
- Docker Compose validated end‑to‑end

### Execution Model & Agent Contract

Mini‑APIRAGORC enforces a strict execution contract between the Executor and Agents.

**Mental rule (keep this in mind):**

- **Executor → passes a `context` dictionary**
- **Agent → reads data from the `context`**
- **Agents never receive raw models directly in production**
- **In manual / local tests → you explicitly simulate the `context`**

This design guarantees:
- strict separation of responsibilities
- agent isolation and testability
- infrastructure‑independent cognition
- fail‑closed behavior by default

Example (manual execution):

```python
context = {
    "incident": kafka_incident
}

result = agent.execute(context)

In production, the context is built by the Executor from Kafka events and metadata.

---

## Current Capabilities

✅ Deterministic execution pipeline  
✅ Kafka‑backed orchestration  
✅ Strict planning schemas (Pydantic v2)  
✅ Retry / abort / continue failure policies  
✅ Fully tested Planner and Executor  
✅ Optional LLM‑based Kafka incident diagnosis  

---

## LLM Usage (Optional)

The system can optionally use an LLM to **diagnose Kafka incidents**.
The LLM is:
- Used by a single agent (`KafkaDiagnosisAgent`)
- Schema‑governed
- Fail‑closed by design
- Never controls execution flow

If the LLM fails or is misconfigured, the system continues operating normally.

Provider‑specific request formats (e.g. Anthropic Claude vs. Nova models)
are fully isolated in the LLM client layer and never leak into agents,
planners, or executors.

---

### LLM Governance & Safety Model

LLM output is treated as untrusted input and is strictly governed by:
- explicit schemas (Pydantic v2)
- deterministic parsing and validation
- controlled normalization (e.g. removal of Markdown fences)
- fail‑closed behavior on any malformed or unexpected output

Only schema‑validated structured data (`DiagnosisResult`) is exposed to the rest of the system.
Raw LLM output is never consumed directly by planners or executors.

---

## Local Setup (Development)

### 1. Create a `.env` file (not committed)

```env
LLM_PROVIDER=bedrock
LLM_MODEL=eu.anthropic.claude-sonnet-4-5-20250929-v1:0
# Example shown for Anthropic Claude on AWS Bedrock.
# Other models may require different request payloads.
LLM_AWS_REGION=eu-south-2
LLM_MAX_TOKENS=1024
LLM_TEMPERATURE=0.2

AWS_ACCESS_KEY_ID=YOUR_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET