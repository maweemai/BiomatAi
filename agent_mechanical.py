"""mechanical_agent: one CrewAI agent."""
from crewai import Agent
from tool_materials import get_material_info, get_tissue_requirements


def create_mechanical_agent(llm) -> Agent:
    return Agent(
        role="Biomechanics Engineer",
        goal="Judge whether each formulation is mechanically appropriate for the target tissue (stiffness, viscoelasticity, porosity, printability).",
        backstory="You compare expected scaffold mechanics with native tissue and state the size of any mismatch.",
        tools=[get_material_info, get_tissue_requirements],
        llm=llm,
        allow_delegation=False,
        max_iter=4,
        verbose=False,
    )
