"""Shared LLM setup: Groq through its OpenAI-compatible endpoint.

Why not the 'groq/...' LiteLLM route? Recent CrewAI versions add a
'cache_breakpoint' field to messages on that route and Groq rejects it.
The 'openai/' + base_url route uses CrewAI's native client, which strips it.

Note: Groq model IDs are case-sensitive and change over time. Current list:
https://console.groq.com/docs/models"""
from crewai import LLM

MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile"]
DEFAULT_MODEL = MODELS[0]
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def get_llm(api_key: str, model: str = DEFAULT_MODEL) -> LLM:
    """The key is passed directly (not via os.environ) so users never share keys."""
    return LLM(
        model=f"openai/{model}",  # first 'openai/' tells CrewAI to use the OpenAI-compatible client
        api_key=api_key,
        base_url=GROQ_BASE_URL,
        temperature=0.2,
        max_tokens=4000,  # reasoning models spend part of this on "thinking"
    )
