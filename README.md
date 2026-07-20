# Careon — AI Career Assistant (FastAPI + React)

Careon is a full-stack AI career assistant — resume ATS scoring, resume
analysis, career path recommendation, learning roadmaps, job description
matching, AI-generated interview questions, and mock interviews with AI
evaluation. Originally prototyped in Streamlit; this is the full-stack
rebuild. The AI/business logic (`services/`, `ai_engine/`, `database/`,
`utils/`) is untouched from the original prototype — only the UI layer
changed, from Streamlit to a proper REST API (FastAPI) + SPA (React).

```
careon/
├── backend/     FastAPI JSON API — all the AI/business logic lives here
└── frontend/    React (Vite) single-page app that talks to the API
```

## Why this structure

- **Backend logic is 1:1 reused.** Everything under `backend/services/`,
  `backend/ai_engine/`, `backend/database/`, `backend/utils/` is copied
  straight from the original project with zero changes to the algorithms —
  ATS scoring, resume analysis, career recommendation, roadmap generation,
  job matching, question generation, and answer evaluation all work exactly
  as before, including the offline fallback when no OpenAI key is set.
- **Session state** — Streamlit's `st.session_state` is replaced by
  `backend/session_store.py`, an in-memory per-session store keyed by an
  `X-Session-Id` header the frontend generates once and reuses. Final
  results are still written through to MongoDB, same as before, and Mongo
  is fully optional — if it can't connect, the app degrades gracefully.

## 1. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and fill in:
#   MONGO_URI        (optional — leave blank to run without persistence)
#   OPENAI_API_KEY    (optional — leave blank to use built-in offline scoring)

uvicorn main:app --reload --port 8000
```

The API is now running at `http://localhost:8000`. Interactive docs are
available at `http://localhost:8000/docs`.

## 2. Frontend setup

In a second terminal:

```bash
cd frontend
npm install

cp .env.example .env
# VITE_API_URL should point at your backend, default http://localhost:8000

npm run dev
```

Open the printed local URL (typically `http://localhost:5173`).

## 3. Production build

```bash
cd frontend
npm run build       # outputs static files to frontend/dist
```

Serve `frontend/dist` with any static host (Netlify, Vercel, nginx, or
`uvicorn` via a StaticFiles mount), and deploy `backend/` separately (e.g.
Render, Railway, Fly.io, or a VM behind gunicorn/uvicorn workers). Set
`VITE_API_URL` to your deployed backend URL before building.

## What's preserved from the original app

- ATS Checker, Resume Analysis (+ skill gap), Career Recommendation,
  Learning Roadmap, Job Match Analyzer, Question Generator (generic +
  personalized), Mock Interview with per-question timer and AI evaluation,
  Final Report, and Career Dashboard — all 10 pages, same flow.
- Same visual identity (warm cream/terracotta palette, cards, badges,
  progress rings) reimplemented in plain CSS instead of Streamlit's theme.
- Same MongoDB collections and schema (`database/*_collection.py`).
- Same offline fallback behavior when OpenAI is unavailable.

## What's different

- Multi-step flows (resume upload → mock interview → report) are now
  driven by explicit API calls instead of Streamlit reruns, so the app
  feels instant and doesn't reload state on every interaction.
- The interview timer, waveform animation, and progress rings are live
  React/CSS instead of Streamlit widgets.
- One backend can now serve multiple frontends (web, and later mobile or
  a browser extension) since it's a clean JSON API.
