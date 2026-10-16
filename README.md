# CareerPilot AI

CareerPilot AI is a Streamlit-based AI career assistant that helps users analyze resumes, compare them with job descriptions, practice interviews, and plan career growth. The app is designed to work in free-tier mode and includes a sample/demo experience when no API key is configured.

## Features

- Resume analyzer for uploaded PDF documents
- Job description matcher with transparent score explanations
- Interview coach with role, interview type, and difficulty controls
- Career roadmap generator based on resume evidence and target role
- Dashboard for quick overview and action shortcuts
- Demo mode that works without API keys

## Tech stack

- Python
- Streamlit
- PyMuPDF
- Pydantic
- Groq (optional)
- pytest

## Project structure

```text
app.py
views/          # page render functions (not named pages/, which Streamlit would auto-load)
components/     # navigation and the shared UI pieces (gauges, chips, roadmap route)
.streamlit/     # theme: colours, fonts, 5 MB upload limit
services/
models/
utils/
assets/
tests/
requirements.txt
.env.example
README.md
```

## Local setup

```bash
cd "C:/Users/venka/OneDrive/Desktop/resume-analysis]"
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Environment configuration

Create a `.env` file in the project root using `.env.example` as a template:

```env
GROQ_API_KEY=your_groq_api_key_here
DEMO_MODE=true
```

For local AI feedback, set `DEMO_MODE=false` after adding a valid key. If `GROQ_API_KEY` is absent, `DEMO_MODE` is true, or a Groq request fails, the app falls back to rule-based analysis so the product remains usable without paid services. Results produced this way are labelled as rule-based feedback, and Groq errors are logged as warnings.

Resume and job-match scores are computed locally by `services/scoring.py`; they are heuristic indicators, not an ATS rating or hiring prediction. With Groq enabled, the model writes resume-review and job-match feedback. Interview questions and evaluations and career roadmaps use built-in rules/templates and do not call Groq.

Resume-review requests send at most 6,000 resume characters and 4,000 job-description characters to Groq; job-match requests send at most 6,000 characters of each input. Resume section contents are not duplicated in the resume-review prompt. Token usage is incurred only for actual Groq requests; the app does not track per-request token counts.

## Demo workflow

1. Open the app.
2. Use the dashboard and available pages.
3. Upload a sample PDF or use the generated demo text.
4. Paste a sample job description.
5. Try the interview practice and roadmap modules.

## Testing

```bash
python -m pytest -q
```

## Deployment

For Streamlit Community Cloud:

1. Push this project to a GitHub repository.
2. Create a Streamlit app pointing to `app.py`.
3. In app secrets, set `GROQ_API_KEY = "your-key"` and `DEMO_MODE = "false"` to enable resume-review and job-match feedback. The Settings page reads deployment secrets but does not edit them.
4. Omit `GROQ_API_KEY` or set `DEMO_MODE = "true"` to use the built-in demo without provider requests.

## Limitations

- Free-tier Groq usage is subject to quota and rate limits.
- The app never fabricates experience, degrees, or achievements; it recommends truthful improvements only.
- Uploaded documents are kept in memory for the running session and are not persisted by default.
- AI-generated recommendations should be treated as decision-support content instead of official ATS or hiring guarantees.

## Security and privacy notes

- Secrets are stored in environment variables and not hardcoded in source files.
- The app does not persist resumes except in local session memory.
- Uploads must parse as PDFs (anything else is rejected) and are limited to 5 MB.
