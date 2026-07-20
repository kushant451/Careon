
import threading
import time

_LOCK = threading.Lock()
_SESSIONS: dict[str, dict] = {}
_SESSION_TTL_SECONDS = 60 * 60 * 6  # 6 hours


def _defaults():
    return {
        "resume_data": None,
        "role": "Software Engineer",
        "questions": [],
        "personalized": False,
        "current_q_index": 0,
        "answers": {},
        "evaluations": {},
        "current_eval": None,
        "interview_started": False,
        "interview_complete": False,
        "q_start_time": None,
        "career_recommendations": None,
        "roadmap_data": None,
        "job_description": "",
        "job_match_result": None,
        "_touched_at": time.time(),
    }


def get_session(session_id: str) -> dict:
    with _LOCK:
        _evict_stale()
        if session_id not in _SESSIONS:
            _SESSIONS[session_id] = _defaults()
        _SESSIONS[session_id]["_touched_at"] = time.time()
        return _SESSIONS[session_id]


def reset_session(session_id: str) -> None:
    with _LOCK:
        _SESSIONS[session_id] = _defaults()


def _evict_stale():
    now = time.time()
    stale = [
        sid for sid, s in _SESSIONS.items()
        if now - s.get("_touched_at", now) > _SESSION_TTL_SECONDS
    ]
    for sid in stale:
        _SESSIONS.pop(sid, None)
