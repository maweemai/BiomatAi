"""Critic agent: short scientific peer review (no tools, so it is cheap)."""
from crewai import Agent


def create_critic_agent(llm) -> Agent:
    return Agent(
        role="Scientific Critic",
        goal="Challenge the conclusions: what is supported by evidence, what is speculation, what is missing.",
        backstory="You are a skeptical peer reviewer. You never simply agree.",
        tools=[],
        llm=llm,
        allow_delegation=False,
        max_iter=3,
        verbose=False,
    )
