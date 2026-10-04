"""Researcher agent: tissue needs, material properties and (optionally) literature."""
from crewai import Agent
from tool_literature import search_literature
from tool_materials import get_material_info, get_tissue_requirements


def create_researcher_agent(llm, use_search: bool = True) -> Agent:
    tools = [get_tissue_requirements, get_material_info]
    if use_search:
        tools.append(search_literature)
    return Agent(
        role="Biomaterials Researcher",
        goal="Summarize target-tissue needs, material properties and key published evidence.",
        backstory="You are a careful scientist. You only cite papers returned by your tools and never invent references.",
        tools=tools,
        llm=llm,
        allow_delegation=False,
        max_iter=8,
        verbose=False,
    )
