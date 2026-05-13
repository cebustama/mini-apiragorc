from typing import Dict, Type


class BaseAgent:
    name: str
    type: str
    inputs: list
    outputs: list

    def execute(self, context: dict):
        """
        Ejecuta el agente usando el contexto compartido.
        Debe lanzar excepciones si falla.
        """
        raise NotImplementedError


# --- Agent Registry ---

AGENTS: Dict[str, Type[BaseAgent]] = {}

def register_agent(agent_cls: Type[BaseAgent]) -> None:
    """
    Registers an agent class by its declared name.
    """
    AGENTS[agent_cls.name] = agent_cls


# --- Concrete agents ---

from swarm.agents.kafka_diagnosis_agent import KafkaDiagnosisAgent

register_agent(KafkaDiagnosisAgent)