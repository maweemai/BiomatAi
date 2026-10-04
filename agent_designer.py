"""Designer agent: formulations, mechanics/degradation fit, experiment matrix."""
from crewai import Agent
from tool_materials import get_material_info, get_tissue_requirements
from tool_doe import generate_factorial_design


def create_designer_agent(llm) -> Agent:
    return Agent(
        role="Biomaterial and Experiment Designer",
        goal="Propose hydrogel formulations, judge their mechanical and degradation fit, and design a lean experiment plan.",
        backstory="You design hydrogels for tissue engineering and lean, statistically sensible experiments for wet-lab researchers.",
        tools=[get_material_info, get_tissue_requirements, generate_factorial_design],
        llm=llm,
        allow_delegation=False,
        max_iter=8,
        verbose=False,
    )
