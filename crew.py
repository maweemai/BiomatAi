"""Assembles agents + tasks into one sequential CrewAI crew."""
from crewai import Crew, Process, Task

from agents.literature_agent import create_literature_agent
from agents.biomaterial_agent import create_biomaterial_agent
from agents.tissue_biology_agent import create_tissue_biology_agent
from agents.mechanical_agent import create_mechanical_agent
from agents.degradation_agent import create_degradation_agent
from agents.experimental_design_agent import create_experimental_design_agent
from agents.critic_agent import create_critic_agent

STEP_NAMES = ["Literature", "Formulations", "Biology", "Mechanics",
              "Degradation", "Experiment plan", "Critic review"]

RULES = ("Be concise (max ~250 words). Use bullet points. Cite only sources returned by "
         "tools; if none are found, say 'no source found'. Never invent references.")


def run_crew(inputs: dict, llm):
    brief = (
        f"Target tissue: {inputs['tissue']}\nTarget cells: {inputs['cells']}\n"
        f"Available materials: {', '.join(inputs['materials'])}\n"
        f"Desired properties: {', '.join(inputs['properties'])}\n"
        f"Fabrication: {inputs['fabrication']}\nNotes: {inputs.get('notes') or 'none'}"
    )

    lit = Task(
        description=f"{brief}\n\nSearch the literature for relevant hydrogel studies. "
                    f"Extract materials, concentrations, crosslinking, properties, cell results. {RULES}",
        expected_output="Bullet list of 3-5 studies with key data and links.",
        agent=create_literature_agent(llm))

    bio = Task(
        description=f"{brief}\n\nPropose 2-3 candidate formulations (materials, approximate "
                    f"concentrations, crosslinking) and give the trade-offs of each. {RULES}",
        expected_output="2-3 formulations, each with rationale, trade-offs and evidence.",
        agent=create_biomaterial_agent(llm), context=[lit])

    tissue = Task(
        description=f"{brief}\n\nAssess biological requirements and risks for each proposed "
                    f"formulation (viability, differentiation, ECM, inflammation). {RULES}",
        expected_output="Per-formulation biological assessment and key readouts.",
        agent=create_tissue_biology_agent(llm), context=[lit, bio])

    mech = Task(
        description=f"{brief}\n\nAssess mechanical suitability of each formulation versus the "
                    f"target tissue. Note stiffness mismatch and printability. {RULES}",
        expected_output="Per-formulation mechanical verdict (suitable / borderline / unsuitable) with reasons.",
        agent=create_mechanical_agent(llm), context=[bio])

    deg = Task(
        description=f"{brief}\n\nAssess swelling and degradation of each formulation and whether "
                    f"it matches tissue regeneration timing. {RULES}",
        expected_output="Per-formulation degradation/swelling assessment and risks.",
        agent=create_degradation_agent(llm), context=[bio])

    doe = Task(
        description=f"{brief}\n\nPick 2-3 key factors from the formulations, then call the "
                    "factorial matrix tool. Add controls, replicates, a characterization plan "
                    f"and failure modes. {RULES}",
        expected_output="Experiment matrix (table), controls, characterization plan, failure modes.",
        agent=create_experimental_design_agent(llm), context=[bio, tissue, mech, deg])

    critic = Task(
        description=f"{brief}\n\nReview all prior work. List: (1) claims supported by evidence, "
                    "(2) unsupported or speculative claims, (3) missing data, (4) the biggest "
                    f"uncertainty to resolve first, (5) overall verdict. {RULES}",
        expected_output="Structured critique with a clear verdict and the single most informative next experiment.",
        agent=create_critic_agent(llm), context=[lit, bio, tissue, mech, deg, doe])

    tasks = [lit, bio, tissue, mech, deg, doe, critic]
    crew = Crew(agents=[t.agent for t in tasks], tasks=tasks,
                process=Process.sequential, max_rpm=20, verbose=False)
    result = crew.kickoff()
    return [t.raw for t in result.tasks_output]
