"""experimental_design_agent: one CrewAI agent."""
from crewai import Agent
from tool_doe import generate_factorial_design


def create_experimental_design_agent(llm) -> Agent:
    return Agent(
        role="Experimental Design Specialist",
        goal="Choose 2-3 key factors and produce an experiment matrix, controls, replicates, characterization plan (SEM, FTIR, mechanical, swelling/degradation, viability) and failure modes.",
        backstory="You design lean, statistically sensible experiments for wet-lab researchers.",
        tools=[generate_factorial_design],
        llm=llm,
        allow_delegation=False,
        max_iter=10,
        verbose=False,
    )
