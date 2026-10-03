"""tissue_biology_agent: one CrewAI agent."""
from crewai import Agent
from tool_materials import get_tissue_requirements
from tool_literature import search_literature


def create_tissue_biology_agent(llm) -> Agent:
    return Agent(
        role="Tissue Biology Specialist",
        goal="Define what the target tissue and cells need (viability, proliferation, differentiation, ECM, inflammation) and flag biological risks of each formulation.",
        backstory="You stop teams from optimizing only mechanics by always checking biological compatibility.",
        tools=[get_tissue_requirements, search_literature],
        llm=llm,
        allow_delegation=False,
        max_iter=10,
        verbose=False,
    )
