from __future__ import annotations

from typing import Dict, Type

from agents.advisory_agent import AdvisoryAgent
from agents.guardrail_agent import GuardrailAgent
from agents.ingestion_agent import IngestionAgent
from agents.quant_agent import QuantAgent
from agents.sentiment_agent import SentimentAgent


class AgentRegistry:
    """Simple registry to build agent instances."""

    def __init__(self) -> None:
        self._registry: Dict[str, Type] = {
            "ingestion": IngestionAgent,
            "sentiment": SentimentAgent,
            "quant": QuantAgent,
            "advisory": AdvisoryAgent,
            "guardrail": GuardrailAgent,
        }

    def create(self, name: str):
        if name not in self._registry:
            raise KeyError(f"Unknown agent: {name}")
        return self._registry[name]()
