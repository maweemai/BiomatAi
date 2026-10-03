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

from config import MODELS, get_llm
from crew import STEP_NAMES, run_crew

st.set_page_config(page_title="Biomaterials Multi-Agent Platform", page_icon="🧬", layout="wide")
st.title("🧬 Biomaterials & Tissue Engineering Multi-Agent Platform")
st.caption("Evidence-grounded decision support, not a replacement for experimental validation.")

# ---- Sidebar: key + model ----
try:
    secret_key = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    secret_key = ""
with st.sidebar:
    api_key = st.text_input("Groq API key", type="password") or secret_key or os.getenv("GROQ_API_KEY", "")
    model = st.selectbox("Groq model", MODELS)
    st.markdown("Get a free key at [console.groq.com](https://console.groq.com/keys).")

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
        st.error("Add a Groq API key in the sidebar.")
    elif not materials or not properties:
        st.error("Select at least one material and one property.")
    else:
        inputs = dict(tissue=tissue, cells=cells, materials=materials,
                      properties=properties, fabrication=fabrication, notes=notes)
        try:
            with st.spinner("7 agents are working (about 1-3 minutes)..."):
                st.session_state["outputs"] = run_crew(inputs, get_llm(api_key, model))
        except Exception as exc:
            st.error(f"Run failed: {exc}")

# ---- Results ----
outputs = st.session_state.get("outputs")
if outputs:
    tabs = st.tabs(STEP_NAMES)
    for tab, name, text in zip(tabs, STEP_NAMES, outputs):
        with tab:
            st.markdown(text)
    report = "\n\n".join(f"## {n}\n\n{t}" for n, t in zip(STEP_NAMES, outputs))
    st.download_button("Download report (.md)", report, "biomaterial_report.md")
