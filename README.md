# Careon — From Resume to Offer

Careon is a full-stack AI-powered career platform that guides job seekers through every step of the hiring process. It scores resumes against ATS systems, recommends career paths, builds learning roadmaps, matches resumes against job descriptions, generates interview questions, runs AI-evaluated mock interviews, and rolls everything up into a final report and dashboard.

Built as a **FastAPI** backend with a **React (Vite)** frontend.

## Live Demo

- **Frontend:** [careon-nine.vercel.app](https://careon-nine.vercel.app)
- **Backend API:** [careon-73ct.onrender.com](https://careon-73ct.onrender.com)

> Note: the backend is hosted on Render's free tier, which spins down when idle. The first request after inactivity may take 30–60 seconds to wake up.

```
careon/
├── backend/     FastAPI REST API — resume parsing, ATS scoring, AI engine, MongoDB persistence
└── frontend/    React (Vite) SPA that consumes the API
```

## Features

- **Resume Upload & Parsing** — accepts PDF/DOCX resumes
- **ATS Checker** — scores a resume against a target role
- **Resume Analysis** — strengths, weaknesses, top skills, AI summary
- **Skill Gap Analyzer** — compares resume skills to role requirements
- **Career Recommendation** — suggests best-fit career paths with match %
- **Learning Roadmap** — week-by-week plan to close skill gaps
- **Job Match Analyzer** — compares a resume against a pasted job description
- **Question Generator** — generic or resume-personalized interview questions
- **Mock Interview** — timed, question-by-question flow with AI evaluation
- **Final Report** — score breakdown, accuracy, and summary
- **Career Dashboard** — overall readiness score

All AI features have an offline fallback (rule-based scoring/generation) when no OpenAI API key is configured.

## Tech Stack

**Backend:** FastAPI, Uvicorn, MongoDB (PyMongo, optional), OpenAI API (optional), pdfplumber, python-docx

**Frontend:** React 19, Vite, React Router, plain CSS

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (optional)
- OpenAI API key (optional)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Fill in MONGO_URI / OPENAI_API_KEY (both optional)

uvicorn main:app --reload --port 8000
```

API runs at `http://localhost:8000`, docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install

cp .env.example .env
# VITE_API_URL should point at your backend (default http://localhost:8000)

npm run dev
```

Open the printed local URL (typically `http://localhost:5173`).

### Production build

```bash
cd frontend
npm run build       # outputs static files to frontend/dist
```

Serve `frontend/dist` with any static host, and deploy `backend/` separately (e.g. Render, Railway, Fly.io).

## Project Structure

```
backend/
├── main.py           # FastAPI app & routes
├── session_store.py  # Per-session state
├── ai_engine/         # LLM client & prompts
├── config/            # Settings, roles, LLM config
├── database/           # MongoDB collections
├── services/            # Core business logic
├── utils/                # Helpers, logging, file handling
└── tests/                 # Unit tests

frontend/
└── src/
    ├── pages/           # One page per feature
    ├── components/       # Sidebar, progress rings, shared UI
    ├── context/            # Global app state
    └── api.js               # API client
```

## Testing

```bash
cd backend
pytest
```