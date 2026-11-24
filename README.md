# GreenRoute — Municipal Waste Truck Routing Agents

A Streamlit educational prototype with an overview dashboard, graph-search route planner (BFS, DFS, UCS, Greedy and A*), capacity-constrained greedy ward allocation, Groq-powered citizen Q&A, analytics and CSV export.

## Run locally
Python 3.10+ recommended.
```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Enable Groq AI
Set the API key privately as an environment variable; never put it in app.py or commit it to GitHub.
macOS/Linux:
```bash
export GROQ_API_KEY="your_private_key"
export GROQ_MODEL="openai/gpt-oss-20b"
streamlit run app.py
```
Windows PowerShell:
```powershell
$env:GROQ_API_KEY="your_private_key"
$env:GROQ_MODEL="openai/gpt-oss-20b"
streamlit run app.py
```
The AI assistant uses Groq's OpenAI-compatible API. Model availability and free-tier quotas are controlled by Groq and may change.

## Deploy
Push this folder to GitHub, then deploy `app.py` through https://share.streamlit.io/. In the app's Secrets settings, add:
```toml
GROQ_API_KEY = "your_private_key"
GROQ_MODEL = "openai/gpt-oss-20b"
```

## Honest prototype limitations
- Ward coordinates, road links, distances and waste figures are illustrative sample data, not verified Bengaluru municipal or live road data.
- Search algorithms run on a small demonstration graph, not live traffic-aware routing.
- Ward allocation uses a priority-first greedy heuristic, not a full CSP/OR-Tools optimiser.
- Citizen AI does not access live municipal databases, official schedules or submit complaints.
- Dashboard analytics are based on sample data, not measured field results.
