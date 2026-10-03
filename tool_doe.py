"""Design-of-experiments tool (pure Python, no extra libraries)."""
import itertools
import json
import math
from crewai.tools import tool

MAX_RUNS = 32


@tool("Generate factorial experiment matrix")
def generate_factorial_design(factors_json: str) -> str:
    """Build a full-factorial experiment matrix.
    Input: a JSON string mapping each factor to a list of 2-3 levels, e.g.
    '{"GelMA %": [5, 10], "Alginate %": [0, 1], "Crosslink time (s)": [30, 60]}'.
    Returns a markdown table of runs (max 32 runs)."""
    try:
        factors = json.loads(factors_json) if isinstance(factors_json, str) else dict(factors_json)
    except Exception as exc:
        return f"Invalid JSON ({exc}). Example: '{{\"GelMA %\": [5, 10], \"Alginate %\": [0, 1]}}'"

    if not factors or any(not isinstance(v, list) or len(v) < 2 for v in factors.values()):
        return "Each factor needs a list of at least 2 levels."

    n_runs = math.prod(len(v) for v in factors.values())
    if n_runs > MAX_RUNS:
        return (f"{n_runs} runs is too many (max {MAX_RUNS}). "
                "Use fewer factors/levels or propose a screening design first.")

    names = list(factors)
    rows = ["| Run | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for i, combo in enumerate(itertools.product(*factors.values()), 1):
        rows.append(f"| {i} | " + " | ".join(str(c) for c in combo) + " |")
    rows.append(f"\nTotal: {n_runs} runs. Add controls and n>=3 replicates per run.")
    return "\n".join(rows)
