Career GPS — Gen-AI Career Platform

Overview

Career GPS is an extensible generative-AI backed platform that helps learners and job-seekers discover career paths, identify skill gaps, and simulate the impact of learning decisions. The project combines lightweight ML/rule-based matching, skill extraction, and a simulation engine to deliver "what-if" scenarios and human-friendly explanations about readiness.

Core Components

- services/
  - `career_matcher.py`: maps user skills to career roles.
  - `skill_extractor.py`: extracts and normalizes skills from text or lists.
  - `skill_gap.py`: analyzes missing, partial, and matched skills for a target career.
  - `readiness_score.py`: computes a readiness score (0-100) and now provides an `explanation` output with next steps.
  - `simulator.py`: what-if simulation engine (switch career, add skills, project-first paths). Added `simulate_what_if_learn` and concise `what_if_summary` outputs.

- utils/
  - `embeddings.py`, `helpers.py`: helper functions, learning time estimates, and utilities.

- app.py
  - Streamlit UI for interactive exploration.
  - Added an optional console conversational layer (activate with `CAREER_GPS_CLI=1`), routed to the internal pipeline.

- app_api.py
  - FastAPI server exposing key endpoints: `/readiness`, `/simulate/learn`, and `/chat` for programmatic integration and to serve as a Gen-AI platform backend.

Getting Started

1. Create and activate a virtual environment (recommended).
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the Streamlit app:

```powershell
streamlit run app.py
```

4. Run the API server:

```powershell
uvicorn app_api:app --reload --port 8000
```

5. Console mode (optional):

```powershell
# On Windows (PowerShell)
$env:CAREER_GPS_CLI = "1"
python app.py
```

Next Steps to make this a fuller Gen-AI Platform

- Add an embeddings-backed vector store and search (e.g., FAISS) for improved semantic matching and retrieval.
- Replace rule-based explanations with an LLM prompt wrapper to produce richer, grounded explanations.
- Add authentication and per-user state persistence (DB) and job history.
- Provide an SDK or client library that wraps the API for easy integration.
- Add more API endpoints: `/recommendations`, `/roadmap`, `/daily-plan`, and webhooks for email notifications.

License

Add a LICENSE file (recommended: MIT) and update repository metadata.
