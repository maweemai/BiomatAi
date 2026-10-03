"""biomaterial_agent: one CrewAI agent."""
from crewai import Agent
from biomat_tools.material_tools import get_material_info
from biomat_tools.literature_tools import search_literature


def create_biomaterial_agent(llm) -> Agent:
    return Agent(
        role="Biomaterial Design Scientist",
        goal="Propose 2-3 candidate hydrogel formulations from the available materials that fit the research objective.",
        backstory="You design hydrogels for tissue engineering and ground every choice in material properties and cited evidence.",
        tools=[get_material_info, search_literature],
        llm=llm,
        allow_delegation=False,
        max_iter=4,
        verbose=False,
    )
