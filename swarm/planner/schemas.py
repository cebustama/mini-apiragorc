from pydantic import BaseModel, Field, conlist
from typing import List, Literal


class ExecutionStep(BaseModel):
    step: int = Field(..., ge=1, description="Sequential step number")
    agent: str = Field(..., description="Name of the agent to execute")
    input_map: List[str] = Field(
        ..., description="References to data available in the execution context"
    )
    failure_policy: Literal["abort", "continue", "retry"] = Field(
        ..., description="Behavior if the step fails"
    )


class PlannerOutput(BaseModel):
    intent: str = Field(..., description="High-level intent of the execution")
    confidence: float = Field(..., ge=0.0, le=1.0)
    plan: conlist(ExecutionStep, min_length=0)


# ---- Internal / validation-only schemas ----

class AgentDescriptor(BaseModel):
    name: str
    type: Literal["deterministic", "cognitive", "generative"]
    inputs: List[str]
    outputs: List[str]


class PlannerInput(BaseModel):
    event: dict
    state: dict
    available_agents: List[AgentDescriptor]
    policies: dict