"""literature_agent: one CrewAI agent."""
from crewai import Agent
from tool_literature import search_literature


def create_literature_agent(llm) -> Agent:
    return Agent(
        role="Biomaterials Literature Analyst",
        goal="Find real papers and extract materials, concentrations, crosslinking, properties and cell results, always with source links.",
        backstory="You are a careful scientific librarian. You only report papers returned by your search tool and never invent references.",
        tools=[search_literature],
        llm=llm,
        allow_delegation=False,
        max_iter=10,
        verbose=False,
    )
