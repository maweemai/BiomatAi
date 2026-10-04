# Biomaterials & Tissue Engineering Multi-Agent Platform

CrewAI + Groq + Streamlit. Seven agents (literature, biomaterial, tissue biology,
mechanical, degradation, experimental design, critic) use tools: Europe PMC literature
search, a local material/tissue knowledge base and a factorial experiment generator.

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```
## Deploy on Streamlit Community Cloud
1. Push this folder to a GitHub repo (never commit your API key).
2. share.streamlit.io > Create app > pick repo, branch, main file `app.py`.
3. Advanced settings: Python 3.12; Secrets: `GROQ_API_KEY = "gsk_..."`.
