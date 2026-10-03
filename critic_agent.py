"""critic_agent: one CrewAI agent."""
from crewai import Agent
from biomat_tools.literature_tools import search_literature


def create_critic_agent(llm) -> Agent:
    return Agent(
        role="Scientific Critic",
        goal="Challenge the team's conclusions: what is supported by evidence, what is speculation, and what is missing.",
        backstory="You are a skeptical peer reviewer. You never simply agree, and you can verify claims with the literature tool.",
        tools=[search_literature],
        llm=llm,
        allow_delegation=False,
        max_iter=4,
        verbose=False,
    )
