
import os
import tempfile
import time
import uuid

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from config.settings import ROLES, DIFFICULTY_LEVELS
from services.resume_parser import extract_text
from services.resume_validator import is_valid_resume
from services.ats_checker import run as ats_run
from services.resume_analyzer import run as analyzer_run
from services.skill_gap_analyzer import analyse as skill_gap_analyse
from services.career_recommender import recommend as career_recommend
from services.roadmap_generator import generate as roadmap_generate
from services.job_match_analyzer import analyze as job_match_analyze
from services.question_generator import generate_generic, generate_personalized
from services.answer_evaluator import evaluate as evaluate_answer
from services.report_generator import build as build_report
from utils.logger import get_logger

from session_store import get_session, reset_session

logger = get_logger(__name__)

app = FastAPI(title="Careon API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _sid(x_session_id: str | None) -> str:
    if not x_session_id:
        raise HTTPException(400, "Missing X-Session-Id header. Call /api/session/new first.")
    return x_session_id


def _avg_score(session: dict) -> float:
    scores = [v["score"] for v in session["evaluations"].values()
              if isinstance(v, dict) and "score" in v]
    return round(sum(scores) / len(scores), 1) if scores else 0.0


# ── best-effort Mongo writes (never break the API if Mongo is unreachable) ──

def _save_resume_to_db(sid, resume):
    try:
        from database.resume_collection import delete_resume, save_resume
        delete_resume(sid)
        save_resume(
            session_id=sid, filename=resume.get("filename", ""),
            raw_text=resume.get("raw_text", ""), role=resume.get("role", ""),
            sections=resume.get("sections", {}), found_skills=resume.get("found_skills", []),
            missing_skills=resume.get("missing_skills", []), ats_score=resume.get("ats_score", 0),
            score_label=resume.get("score_label", ""), suggestions=resume.get("suggestions", []),
            strengths=resume.get("strengths", []), weaknesses=resume.get("weaknesses", []),
            top_skills=resume.get("top_skills", []), summary=resume.get("summary", ""),
        )
    except Exception as exc:
        logger.warning("Mongo save_resume skipped: %s", exc)


def _save_career_rec_to_db(sid, result):
    try:
        from database.career_collection import save_career_recommendation
        save_career_recommendation(
            session_id=sid, role=result.get("primary_role", ""),
            top_matches=result.get("top_matches", []), insight=result.get("insight", ""),
        )
    except Exception as exc:
        logger.warning("Mongo save_career_recommendation skipped: %s", exc)


def _save_roadmap_to_db(sid, result):
    try:
        from database.career_collection import save_roadmap
        save_roadmap(
            session_id=sid, role=result.get("role", ""), weeks=result.get("weeks", 0),
            milestones=result.get("milestones", []), total_skills=result.get("total_skills", 0),
            generated_by_ai=result.get("generated_by_ai", False),
        )
    except Exception as exc:
        logger.warning("Mongo save_roadmap skipped: %s", exc)


def _save_job_match_to_db(sid, role, jd, result):
    try:
        from database.career_collection import save_job_match
        save_job_match(
            session_id=sid, role=role, job_description=jd,
            match_percent=result.get("match_percent", 0),
            matched_keywords=result.get("matched_keywords", []),
            missing_keywords=result.get("missing_keywords", []),
            summary=result.get("summary", ""),
        )
    except Exception as exc:
        logger.warning("Mongo save_job_match skipped: %s", exc)


def _save_history_to_db(sid, report):
    try:
        from database.history_collection import save_history
        save_history(
            session_id=sid, role=report.get("role", ""), ats_score=report.get("ats_score", 0),
            interview_score=report.get("overall_score", 0),
            total_questions=report.get("total_questions", 0), attempted=report.get("attempted", 0),
            accuracy=report.get("accuracy", 0), breakdown=report.get("breakdown", {}),
            summary=report.get("summary", ""),
        )
    except Exception as exc:
        logger.warning("Mongo save_history skipped: %s", exc)


def _mock_interview_start(sid, role, questions, personalized):
    try:
        from services.mock_interview import start_session
        start_session(sid, role, questions, personalized)
    except Exception as exc:
        logger.warning("Mongo interview start skipped: %s", exc)


def _mock_interview_record(sid, index, answer, evaluation):
    try:
        from services.mock_interview import record_answer, advance
        record_answer(sid, index, answer, evaluation)
        advance(sid, index + 1)
    except Exception as exc:
        logger.warning("Mongo interview record skipped: %s", exc)


def _mock_interview_end(sid):
    try:
        from services.mock_interview import end_session
        end_session(sid)
    except Exception as exc:
        logger.warning("Mongo interview end skipped: %s", exc)


# ─────────────────────────────  session  ────────────────────────────────

@app.post("/api/session/new")
def new_session():
    sid = str(uuid.uuid4())
    get_session(sid)
    return {"session_id": sid}


@app.post("/api/session/reset")
def reset(x_session_id: str | None = Header(default=None)):
    sid = _sid(x_session_id)
    reset_session(sid)
    return {"ok": True}


@app.get("/api/meta")
def meta():
    return {"roles": ROLES, "difficulty_levels": DIFFICULTY_LEVELS}


# ─────────────────────────────  resume  ─────────────────────────────────

@app.post("/api/resume/upload")
async def upload_resume(
    x_session_id: str | None = Header(default=None),
    role: str = Form(...),
    file: UploadFile = File(...),
):
    sid = _sid(x_session_id)
    session = get_session(sid)

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("pdf", "docx"):
        raise HTTPException(400, "Please upload a PDF or DOCX file.")

    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        try:
            text = extract_text(tmp_path, file.filename)
        except ValueError as exc:
            raise HTTPException(400, str(exc))
    finally:
        os.unlink(tmp_path)

    valid, reason = is_valid_resume(text)
    if not valid:
        raise HTTPException(400, reason)

    ats = ats_run(text, role)
    analysis = analyzer_run(text, role, ats["found_skills"], ats["missing_skills"], ats["sections"])

    resume_data = {
        "filename": file.filename,
        "role": role,
        "raw_text": text,
        **ats,
        **analysis,
    }
    session["resume_data"] = resume_data
    session["role"] = role
    _save_resume_to_db(sid, resume_data)

    return resume_data


@app.get("/api/resume")
def get_resume(x_session_id: str | None = Header(default=None)):
    session = get_session(_sid(x_session_id))
    return session["resume_data"]


# ─────────────────────────────  career  ─────────────────────────────────

@app.post("/api/career/recommend")
def career_recommend_route(x_session_id: str | None = Header(default=None)):
    sid = _sid(x_session_id)
    session = get_session(sid)
    resume = session["resume_data"]
    if not resume:
        raise HTTPException(400, "Upload a resume first.")
    result = career_recommend(
        resume.get("role", session["role"]),
        resume.get("found_skills", []),
        resume.get("top_skills", []),
    )
    session["career_recommendations"] = result
    _save_career_rec_to_db(sid, result)
    return result


@app.get("/api/career")
def career_get(x_session_id: str | None = Header(default=None)):
    session = get_session(_sid(x_session_id))
    return session["career_recommendations"]


# ─────────────────────────────  roadmap  ─────────────────────────────────

class RoadmapRequest(BaseModel):
    role: str
    weeks: int = 8


@app.post("/api/roadmap/generate")
def roadmap_generate_route(body: RoadmapRequest, x_session_id: str | None = Header(default=None)):
    sid = _sid(x_session_id)
    session = get_session(sid)
    resume = session["resume_data"]
    missing = resume.get("missing_skills", []) if resume else []
    result = roadmap_generate(body.role, missing, body.weeks)
    session["roadmap_data"] = result
    session["role"] = body.role
    _save_roadmap_to_db(sid, result)
    return result


@app.get("/api/roadmap")
def roadmap_get(x_session_id: str | None = Header(default=None)):
    session = get_session(_sid(x_session_id))
    return session["roadmap_data"]


@app.get("/api/roadmap/download", response_class=PlainTextResponse)
def roadmap_download(x_session_id: str | None = Header(default=None)):
    session = get_session(_sid(x_session_id))
    result = session["roadmap_data"]
    if not result:
        raise HTTPException(404, "No roadmap generated yet.")
    lines = [f"LEARNING ROADMAP — {result['role']} ({result['weeks']} weeks)", "=" * 50, ""]
    for m in result.get("milestones", []):
        lines.append(f"Week {m.get('week')}: {m.get('title')}")
        for t in m.get("tasks", []):
            lines.append(f"  - {t}")
        lines.append("")
    return "\n".join(lines)


# ─────────────────────────────  job match  ───────────────────────────────

class JobMatchRequest(BaseModel):
    role: str
    job_description: str


@app.post("/api/jobmatch/analyze")
def jobmatch_analyze_route(body: JobMatchRequest, x_session_id: str | None = Header(default=None)):
    sid = _sid(x_session_id)
    session = get_session(sid)
    resume = session["resume_data"]
    if not resume:
        raise HTTPException(400, "Upload a resume first.")
    if not body.job_description.strip():
        raise HTTPException(400, "Please paste a job description first.")
    result = job_match_analyze(resume.get("raw_text", ""), body.job_description, body.role)
    session["job_description"] = body.job_description
    session["job_match_result"] = result
    _save_job_match_to_db(sid, body.role, body.job_description, result)
    return result


@app.get("/api/jobmatch")
def jobmatch_get(x_session_id: str | None = Header(default=None)):
    session = get_session(_sid(x_session_id))
    return {
        "result": session["job_match_result"],
        "job_description": session["job_description"],
    }


# ─────────────────────────────  questions  ───────────────────────────────

class QuestionsRequest(BaseModel):
    role: str
    difficulty: str = "All Levels"
    count: int = 10
    personalized: bool = False


@app.post("/api/questions/generate")
def questions_generate_route(body: QuestionsRequest, x_session_id: str | None = Header(default=None)):
    sid = _sid(x_session_id)
    session = get_session(sid)

    if body.personalized:
        resume = session["resume_data"]
        if not resume:
            raise HTTPException(400, "Upload a resume first to generate personalized questions.")
        qs = generate_personalized(
            body.role, resume.get("found_skills", []), resume.get("top_skills", [])[:5], body.count
        )
    else:
        qs = generate_generic(body.role, body.difficulty, body.count)

    session["questions"] = qs
    session["role"] = body.role
    session["personalized"] = body.personalized
    return {"questions": qs, "role": body.role, "personalized": body.personalized}


@app.get("/api/questions")
def questions_get(x_session_id: str | None = Header(default=None)):
    session = get_session(_sid(x_session_id))
    return {
        "questions": session["questions"],
        "role": session["role"],
        "personalized": session["personalized"],
    }


@app.get("/api/questions/download", response_class=PlainTextResponse)
def questions_download(x_session_id: str | None = Header(default=None)):
    session = get_session(_sid(x_session_id))
    questions = session["questions"]
    if not questions:
        raise HTTPException(404, "No questions generated yet.")
    lines = [f"Interview Questions — {session['role']}", "=" * 44, ""] + [
        f"{i}. [{q.get('category')}] [{q.get('difficulty')}] {q['question']}"
        for i, q in enumerate(questions, 1)
    ]
    return "\n".join(lines)


# ─────────────────────────────  mock interview  ──────────────────────────

@app.post("/api/interview/start")
def interview_start(x_session_id: str | None = Header(default=None)):
    sid = _sid(x_session_id)
    session = get_session(sid)
    questions = session["questions"]
    if not questions:
        raise HTTPException(400, "No questions loaded. Generate questions first.")
    session["current_q_index"] = 0
    session["answers"] = {}
    session["evaluations"] = {}
    session["interview_started"] = True
    session["interview_complete"] = False
    session["q_start_time"] = time.time()
    _mock_interview_start(sid, session["role"], questions, session["personalized"])
    return _interview_state(session)


def _interview_state(session):
    idx = session["current_q_index"]
    questions = session["questions"]
    total = len(questions)
    done = idx >= total
    return {
        "index": idx,
        "total": total,
        "done": done,
        "question": questions[idx] if not done else None,
        "role": session["role"],
        "personalized": session["personalized"],
        "q_start_time": session["q_start_time"],
    }


@app.get("/api/interview")
def interview_get(x_session_id: str | None = Header(default=None)):
    session = get_session(_sid(x_session_id))
    return _interview_state(session)


class AnswerRequest(BaseModel):
    index: int
    answer: str


@app.post("/api/interview/answer")
def interview_answer(body: AnswerRequest, x_session_id: str | None = Header(default=None)):
    sid = _sid(x_session_id)
    session = get_session(sid)
    questions = session["questions"]
    if body.index < 0 or body.index >= len(questions):
        raise HTTPException(400, "Invalid question index.")
    if not body.answer.strip():
        raise HTTPException(400, "Please write an answer before submitting.")

    question = questions[body.index]
    evaluation = evaluate_answer(question["question"], body.answer, session["role"], question.get("keywords"))

    session["answers"][body.index] = body.answer
    session["evaluations"][body.index] = evaluation
    _mock_interview_record(sid, body.index, body.answer, evaluation)

    session["current_eval"] = {
        "question": question, "answer": body.answer, "evaluation": evaluation,
        "idx": body.index, "total": len(questions),
    }
    session["current_q_index"] = body.index + 1
    session["q_start_time"] = time.time()

    return session["current_eval"]


@app.get("/api/interview/current-eval")
def interview_current_eval(x_session_id: str | None = Header(default=None)):
    session = get_session(_sid(x_session_id))
    return session["current_eval"]


@app.post("/api/interview/end")
def interview_end(x_session_id: str | None = Header(default=None)):
    sid = _sid(x_session_id)
    session = get_session(sid)
    session["interview_complete"] = True
    _mock_interview_end(sid)
    return {"ok": True}


# ─────────────────────────────  report  ───────────────────────────────────

@app.get("/api/report")
def report_get(x_session_id: str | None = Header(default=None)):
    sid = _sid(x_session_id)
    session = get_session(sid)
    interview = {
        "role": session["role"],
        "personalized": session["personalized"],
        "questions": session["questions"],
        "answers": {str(k): v for k, v in session["answers"].items()},
        "evaluations": {str(k): v for k, v in session["evaluations"].items()},
    }
    report = build_report(interview, session["resume_data"])
    report["evaluations"] = interview["evaluations"]
    if report.get("attempted", 0) > 0:
        _save_history_to_db(sid, report)
    return report


@app.get("/api/report/download", response_class=PlainTextResponse)
def report_download(x_session_id: str | None = Header(default=None)):
    session = get_session(_sid(x_session_id))
    interview = {
        "role": session["role"],
        "personalized": session["personalized"],
        "questions": session["questions"],
        "answers": {str(k): v for k, v in session["answers"].items()},
        "evaluations": {str(k): v for k, v in session["evaluations"].items()},
    }
    report = build_report(interview, session["resume_data"])
    if report.get("attempted", 0) == 0:
        raise HTTPException(404, "No interview data yet.")
    lines = [
        "AI INTERVIEW PREP — FINAL REPORT", "=" * 50,
        f"Role          : {report.get('role', '-')}",
        f"Overall Score : {report.get('overall_score', 0)}/10  {report.get('stars', '')}",
        f"Performance   : {report.get('performance_label', '-')}",
        f"ATS Score     : {report.get('ats_score', 0)}/100",
        f"Accuracy      : {report.get('accuracy', 0)}%", "",
        "Score Breakdown:",
    ] + [f"  {k}: {v}/10" for k, v in report.get("breakdown", {}).items()] + [
        "", "Summary:", report.get("summary", "")
    ]
    return "\n".join(lines)


# ─────────────────────────────  dashboard  ────────────────────────────────

@app.get("/api/dashboard")
def dashboard_get(x_session_id: str | None = Header(default=None)):
    session = get_session(_sid(x_session_id))
    resume = session["resume_data"]
    ats = resume.get("ats_score", 0) if resume else 0
    mock_avg = _avg_score(session)
    career = session["career_recommendations"]
    roadmap = session["roadmap_data"]
    jobmatch = session["job_match_result"]

    top_path = career["top_matches"][0] if career and career.get("top_matches") else None
    top_pct = top_path["match_percent"] if top_path else 0
    jm_pct = jobmatch["match_percent"] if jobmatch else 0

    readiness = round(ats * 0.25 + mock_avg * 10 * 0.35 + top_pct * 0.2 + jm_pct * 0.2)

    return {
        "readiness": readiness,
        "ats_score": ats,
        "mock_avg": mock_avg,
        "top_career": {"title": top_path["title"], "match_percent": top_pct} if top_path else None,
        "job_match_percent": jm_pct if jobmatch else None,
        "roadmap_summary": (
            {"weeks": roadmap["weeks"], "role": roadmap["role"],
             "total_skills": roadmap["total_skills"], "milestones": len(roadmap.get("milestones", []))}
            if roadmap else None
        ),
        "top_career_matches": (career.get("top_matches", [])[:3] if career else []),
    }


# ─────────────────────────────  skill gap (used by analysis page)  ────────

@app.get("/api/skillgap")
def skillgap_get(x_session_id: str | None = Header(default=None)):
    session = get_session(_sid(x_session_id))
    resume = session["resume_data"]
    if not resume:
        raise HTTPException(400, "Upload a resume first.")
    return skill_gap_analyse(resume["role"], resume.get("found_skills", []), resume.get("missing_skills", []))
