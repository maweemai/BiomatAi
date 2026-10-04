# Streamlit Cloud ships an old sqlite3; crewai's dependencies need a newer one.
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import os
os.environ.setdefault("OTEL_SDK_DISABLED", "true")  # turn off CrewAI telemetry

import streamlit as st

import limits
from config import MODELS, get_llm
from crew import STEP_NAMES, run_crew

st.set_page_config(page_title="Biomaterials Multi-Agent Platform", page_icon="🧬", layout="wide")
st.title("🧬 Biomaterials & Tissue Engineering Multi-Agent Platform")
st.caption("Evidence-grounded decision support, not a replacement for experimental validation.")

RATE_WORDS = ("rate limit", "rate_limit", "error code: 429", "tokens per")


def is_rate_limit(exc) -> bool:
    return any(w in str(exc).lower() for w in RATE_WORDS)


def is_tool_glitch(exc) -> bool:
    """gpt-oss sometimes tries a tool it does not have; a retry usually works."""
    return "tool_use_failed" in str(exc)


def run_with_fallback(inputs, key, model, use_search, use_critic):
    """Retry up to 3 times. Groq limits are per model, so alternate between models."""
    others = [m for m in MODELS if m != model]
    last = None
    for m in ([model] + others + [model])[:3]:
        try:
            return run_crew(inputs, get_llm(key, m), use_search, use_critic)
        except Exception as exc:
            last = exc
            if not (is_rate_limit(exc) or is_tool_glitch(exc)):
                raise
    raise last


# ---- Sidebar ----
try:
    secret_key = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    secret_key = ""
with st.sidebar:
    own = st.text_input("Your own Groq key (optional)", type="password")
    own_key = bool(own.strip())
    api_key = own.strip() or secret_key or os.getenv("GROQ_API_KEY", "")
    model = st.selectbox("Groq model", MODELS)
    use_search = st.checkbox("Search literature (uses more tokens)", value=True)
    use_critic = st.checkbox("Include critic review (uses more tokens)", value=False)
    if own_key:
        st.caption("Using your own key: no app limits.")
    else:
        st.caption(f"Shared free runs left today: {limits.runs_left_today()}")
        st.caption(f"Your runs this visit: {st.session_state.get('runs_done', 0)}/{limits.SESSION_MAX_RUNS}")
    st.markdown("Free key: [console.groq.com](https://console.groq.com/keys)")

# ---- Inputs ----
col1, col2 = st.columns(2)
with col1:
    tissue = st.selectbox("Target tissue", ["Cartilage", "Bone", "Skin", "Muscle", "Cardiac", "Neural"])
    cells = st.text_input("Target cells", "Chondrocytes")
    fabrication = st.selectbox("Fabrication", ["Hydrogel casting", "Extrusion bioprinting", "Electrospinning"])
with col2:
    materials = st.multiselect("Available materials",
                               ["GelMA", "Alginate", "Chitosan", "Collagen", "Hyaluronic acid", "PEG"],
                               default=["GelMA", "Alginate", "Hyaluronic acid"])
    properties = st.multiselect("Desired properties",
                                ["Mechanical stability", "High cell viability", "Controlled degradation",
                                 "Printability", "Bioactivity"],
                                default=["Mechanical stability", "High cell viability", "Controlled degradation"])
notes = st.text_area("Extra notes (optional)")

if st.button("Run multi-agent analysis", type="primary"):
    if not api_key:
        st.error("No API key available. Paste your own Groq key in the sidebar.")
    elif not materials or not properties:
        st.error("Select at least one material and one property.")
    else:
        inputs = dict(tissue=tissue, cells=cells, materials=materials,
                      properties=properties, fabrication=fabrication, notes=notes)
        ck = limits.cache_key(inputs, use_search, use_critic)
        cached = limits.cache_get(ck)
        if cached:
            st.session_state["outputs"] = cached
            st.info("Showing a saved result for identical inputs (no tokens used).")
        else:
            msg = None if own_key else limits.check_shared_limits()
            if msg:
                st.warning(msg)
            elif not limits.try_acquire():
                st.warning("The app is busy with other users. Please try again in about a minute.")
            else:
                try:
                    if not own_key:
                        limits.register_run()
                    with st.spinner("Agents are working (about 1 minute)..."):
                        outputs = run_with_fallback(inputs, api_key, model, use_search, use_critic)
                    st.session_state["outputs"] = outputs
                    limits.cache_put(ck, outputs)
                except Exception as exc:
                    if is_tool_glitch(exc):
                        st.warning("The AI model made a tool-calling mistake. Please click Run again. "
                                   "Unticking the critic review in the sidebar also helps.")
                    elif is_rate_limit(exc):
                        st.warning("The free quota is busy or used up right now. Wait a few minutes "
                                   "and try again, or paste your own free Groq key in the sidebar.")
                    else:
                        st.error(f"Run failed: {exc}")
                finally:
                    limits.release()

# ---- Results ----
outputs = st.session_state.get("outputs")
if outputs:
    names = STEP_NAMES[:len(outputs)]
    tabs = st.tabs(names)
    for tab, name, text in zip(tabs, names, outputs):
        with tab:
            st.markdown(text)
    report = "\n\n".join(f"## {n}\n\n{t}" for n, t in zip(names, outputs))
    st.download_button("Download report (.md)", report, "biomaterial_report.md")
