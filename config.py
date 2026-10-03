"""Shared LLM setup (Groq via CrewAI's LLM class / LiteLLM)."""
from crewai import LLM

# Groq retires model IDs from time to time: check https://console.groq.com/docs/models
MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
DEFAULT_MODEL = MODELS[0]


def get_llm(api_key: str, model: str = DEFAULT_MODEL) -> LLM:
    """Build a Groq-backed LLM. The key is passed directly (not via os.environ)
    so concurrent users of a deployed app never share keys."""
    return LLM(
        model=f"groq/{model}",
        api_key=api_key,
        temperature=0.2,
        max_tokens=1500,
    )
