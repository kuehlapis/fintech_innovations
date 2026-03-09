import logging
from pathlib import Path
from typing import Optional, Type, TypeVar

import yaml
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from utils.config import getConfig

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:  # pragma: no cover - optional dependency
    ChatGoogleGenerativeAI = None

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


class PromptLoader:
    """Load prompts from a YAML file with a simple fallback mechanism."""

    def __init__(self, prompt_path: str):
        self.prompt_path = Path(prompt_path)

    def get_prompt(self, agent_type: str) -> str:
        if not self.prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {self.prompt_path}")

        with self.prompt_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        prompts = data.get("prompts", {})
        base_prompt = prompts.get("base", "")
        return prompts.get(agent_type, base_prompt)


class BaseAgent:
    """Base class for LLM-backed agents with prompt and schema support."""

    def __init__(
        self,
        agent_type: str,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> None:
        self.agent_type = agent_type
        self.config = getConfig(validate=False)
        self.api_key = self.config.get_gemini_api_key()

        self.model_name = model_name or self.config.get_gemini_model()
        self.temperature = (
            self.config.get_gemini_temperature()
            if temperature is None
            else temperature
        )

        self.prompt_loader = PromptLoader(self.config.get_prompt_path())
        self.system_prompt = self.prompt_loader.get_prompt(agent_type)

        self.prompt = ChatPromptTemplate.from_messages(
            [("system", "{system_prompt}"), ("human", "{input}")]
        )

        self.client = self._build_client()

    def _build_client(self):
        if not self.api_key or not ChatGoogleGenerativeAI:
            logger.warning("[%s] LLM client not configured", self.agent_type)
            return None
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=self.temperature,
        )

    def run_text(self, input_text: str) -> str:
        """Run the agent and return a raw text response."""
        if not self.client:
            return "LLM unavailable."

        chain = self.prompt | self.client
        response = chain.invoke({"system_prompt": self.system_prompt, "input": input_text})
        return getattr(response, "content", str(response))

    def run_structured(self, input_text: str, schema: Type[T]) -> T:
        """Run the agent and return a structured response."""
        if not self.client:
            return schema()  # type: ignore[call-arg]

        structured_client = self.client.with_structured_output(schema)
        chain = self.prompt | structured_client
        response: T = chain.invoke({"system_prompt": self.system_prompt, "input": input_text})
        return response