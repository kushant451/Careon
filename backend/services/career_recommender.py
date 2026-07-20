import json
from pathlib import Path
from ai_engine import llm_client, prompt_templates
from config.llm_config import LLM_TEMPERATURE_ANALYSIS

DATA_DIR = Path(__file__).parent.parent / "data"
with open(DATA_DIR / "career_paths.json", encoding="utf-8") as f:
    CAREER_PATHS = json.load(f)


def _match_percent(user_skills_lower, core_skills):
    if not core_skills:
        return 0
    hits = sum(1 for s in core_skills if s.lower() in user_skills_lower)
    return round((hits / len(core_skills)) * 100)


def _matched_missing(user_skills_lower, core_skills):
    matched, missing = [], []
    for cs in core_skills:
        (matched if cs.lower() in user_skills_lower else missing).append(cs)
    return matched, missing


def rank_paths(user_skills, top_n=6):
    user_lower = {s.lower() for s in user_skills}
    ranked = []
    for path in CAREER_PATHS:
        pct = _match_percent(user_lower, path["core_skills"])
        matched, missing = _matched_missing(user_lower, path["core_skills"])
        ranked.append({
            **path,
            "match_percent": pct,
            "matched_skills": matched,
            "missing_skills": missing,
        })
    ranked.sort(key=lambda p: p["match_percent"], reverse=True)
    return ranked[:top_n]


def _ai_insight(role, top_path, user_skills):
    prompt = prompt_templates.career_recommendation_prompt(
        role, user_skills, top_path["title"], top_path["core_skills"]
    )
    reply = llm_client.chat(prompt, temperature=LLM_TEMPERATURE_ANALYSIS)
    if reply and len(reply.strip()) > 20:
        return reply.strip()
    return (
        f"Based on your current skill set, {top_path['title']} is your strongest match "
        f"({top_path['match_percent']}% skill overlap). Focus on closing the remaining "
        f"skill gaps below to strengthen your candidacy for this path."
    )


def recommend(role, found_skills, top_skills=None):
    """Rank suitable career paths for a candidate based on their resume skills."""
    user_skills = list(dict.fromkeys((found_skills or []) + (top_skills or [])))
    if not user_skills:
        return {"top_matches": [], "insight": "Upload a resume to get personalised career recommendations.",
                "primary_role": role}

    ranked = rank_paths(user_skills)
    insight = _ai_insight(role, ranked[0], user_skills) if ranked else ""
    return {"top_matches": ranked, "insight": insight, "primary_role": role}