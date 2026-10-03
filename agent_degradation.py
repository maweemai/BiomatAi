"""degradation_agent: one CrewAI agent."""
from crewai import Agent
from tool_materials import get_material_info
from tool_literature import search_literature


def create_degradation_agent(llm) -> Agent:
    return Agent(
        role="Degradation and Stability Analyst",
        goal="Evaluate swelling, hydrolytic/enzymatic degradation and mechanical retention, and whether degradation matches tissue regeneration.",
        backstory="You think about crosslink density, mass loss and how long a scaffold must last in the body.",
        tools=[get_material_info, search_literature],
        llm=llm,
        allow_delegation=False,
        max_iter=4,
        verbose=False,
    )
