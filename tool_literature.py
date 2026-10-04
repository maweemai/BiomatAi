"""Literature tool: Europe PMC REST API (free, no API key)."""
import re
import requests
from crewai.tools import tool

EPMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


@tool("Search biomaterials literature")
def search_literature(query: str) -> str:
    """Search Europe PMC (PubMed, PMC and preprints) for papers.
    Input: a short keyword query, e.g. 'GelMA alginate cartilage bioprinting'.
    Returns up to 3 papers with title, year, journal, link and abstract excerpt."""
    try:
        resp = requests.get(
            EPMC_URL,
            params={"query": query, "format": "json", "resultType": "core", "pageSize": 3},
            timeout=20,
        )
        resp.raise_for_status()
        results = resp.json().get("resultList", {}).get("result", [])
    except Exception as exc:  # errors are returned to the agent as text
        return f"Literature search failed: {exc}"

    if not results:
        return "No papers found. Try a shorter or different query."

    out = []
    for i, r in enumerate(results, 1):
        abstract = re.sub(r"<[^>]+>", "", r.get("abstractText", "") or "")[:250]
        link = f"https://europepmc.org/article/{r.get('source', 'MED')}/{r.get('id', '')}"
        out.append(
            f"[{i}] {r.get('title', 'No title')} ({r.get('pubYear', 'n.d.')}), "
            f"{r.get('journalTitle', 'n/a')}\n    Link: {link}\n    Abstract: {abstract or 'n/a'}"
        )
    out.append("\nNOTE: Use these results now. Do NOT search again; write your final answer.")
    return "\n".join(out)
