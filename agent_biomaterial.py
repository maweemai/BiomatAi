"""biomaterial_agent: one CrewAI agent."""
from crewai import Agent
from tool_materials import get_material_info
from tool_literature import search_literature


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
