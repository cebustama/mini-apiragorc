from pydantic import BaseModel, Field
from typing import List


class KafkaIncident(BaseModel):
    error: str = Field(..., description="Primary error message")
    topic: str | None = Field(None)
    consumer_group: str | None = Field(None)
    lag: int | None = Field(None, ge=0)
    brokers_status: dict | None = Field(
        None, description="Broker -> status mapping"
    )


class ProbableCause(BaseModel):
    code: str = Field(..., description="Stable cause identifier")
    description: str = Field(..., description="Human-readable explanation")
    confidence: float = Field(..., ge=0.0, le=1.0)


class DiagnosisResult(BaseModel):
    causes: List[ProbableCause] = Field(default_factory=list)