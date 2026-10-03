"""Shared LLM setup: Groq through its OpenAI-compatible endpoint.

Why not the 'groq/...' LiteLLM route? Recent CrewAI versions add a
'cache_breakpoint' field to messages on that route and Groq rejects it.
The 'openai/' + base_url route uses CrewAI's native client, which strips it."""
from crewai import LLM

# Groq retires model IDs from time to time: check https://console.groq.com/docs/models
MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
DEFAULT_MODEL = MODELS[0]
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def get_llm(api_key: str, model: str = DEFAULT_MODEL) -> LLM:
    """The key is passed directly (not via os.environ) so users never share keys."""
    return LLM(
        model=f"openai/{model}",
        api_key=api_key,
        base_url=GROQ_BASE_URL,
        temperature=0.2,
        max_tokens=1500,
    )
