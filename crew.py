"""Lean crew: Researcher -> Designer -> (optional) Critic. Few steps = few tokens."""
from crewai import Crew, Process, Task

from agent_researcher import create_researcher_agent
from agent_designer import create_designer_agent
from agent_critic import create_critic_agent

STEP_NAMES = ["Research", "Design & experiments", "Critic review"]

RULES = ("Be concise and use bullet points. Cite only sources returned by tools "
         "(say 'no source found' otherwise); never invent references. Call each tool "
         "at most 2 times, then STOP calling tools and write your final answer in plain text. "
         "You have NO code, shell, container or browser tools: only call tools that are "
         "explicitly listed for you, and never call container.exec, python or browser tools.")


def run_crew(inputs: dict, llm, use_search: bool = True, use_critic: bool = True):
    brief = (
        f"Tissue: {inputs['tissue']}; cells: {inputs['cells']}; "
        f"materials: {', '.join(inputs['materials'])}; "
        f"desired: {', '.join(inputs['properties'])}; fabrication: {inputs['fabrication']}; "
        f"notes: {inputs.get('notes') or 'none'}"
    )

    research = Task(
        description=(
            f"{brief}\n\nCall get_tissue_requirements once. Call get_material_info once with ALL "
            "materials as a comma-separated list. "
            + ("Run ONE literature search with a short query. " if use_search else "")
            + f"Then write max 180 words: tissue needs, pros/cons per material"
            + (", and 2-3 papers with links. " if use_search else ". ") + RULES),
        expected_output="Under 180 words: tissue needs, material pros/cons" + (", papers with links." if use_search else "."),
        agent=create_researcher_agent(llm, use_search))

    design = Task(
        description=(
            f"{brief}\n\nUsing the research notes, write max 250 words: (1) two candidate "
            "formulations (materials, approximate %, crosslinking); (2) for each, mechanical fit "
            "vs the tissue and expected degradation; (3) key trade-offs. Then call "
            "generate_factorial_design once with at most 3 factors x 2 levels, and add controls, "
            "replicates and a short characterization list (SEM, FTIR, mechanics, swelling, viability). "
            + RULES),
        expected_output="Formulations, trade-offs, experiment matrix table, controls, characterization list.",
        agent=create_designer_agent(llm), context=[research])

    tasks = [research, design]
    if use_critic:
        tasks.append(Task(
            description=(
                "Review the work so far in max 120 words: supported claims, speculative claims, "
                "missing data, biggest uncertainty, verdict, and the single most informative next "
                "experiment. " + RULES),
            expected_output="Short critique with verdict and next experiment.",
            agent=create_critic_agent(llm), context=[research, design]))

    crew = Crew(agents=[t.agent for t in tasks], tasks=tasks,
                process=Process.sequential, max_rpm=20, verbose=False)
    result = crew.kickoff()
    return [t.raw for t in result.tasks_output]
