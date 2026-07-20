import json, re
from pathlib import Path
from ai_engine import llm_client, prompt_templates
from config.llm_config import LLM_TEMPERATURE_ANALYSIS

DATA_DIR = Path(__file__).parent.parent / "data"
with open(DATA_DIR / "skills_data.json", encoding="utf-8") as f:
    SKILLS_DATA = json.load(f)


def _all_known_skills():
    seen, out = set(), []
    for skills in SKILLS_DATA.values():
        for s in skills:
            if s.lower() not in seen:
                seen.add(s.lower())
                out.append(s)
    return out


ALL_SKILLS = _all_known_skills()


def _extract_keywords(text):
    lower = text.lower()
    return [s for s in ALL_SKILLS if re.search(r"\b" + re.escape(s.lower()) + r"\b", lower)]


def _verdict(pct):
    if pct >= 75:
        return "Excellent Match", "b-green"
    if pct >= 50:
        return "Good Match", "b-yellow"
    if pct >= 25:
        return "Partial Match", "b-yellow"
    return "Low Match", "b-red"


def _ai_summary(role, matched, missing, pct):
    prompt = prompt_templates.job_match_prompt(role, matched, missing, pct)
    reply = llm_client.chat(prompt, temperature=LLM_TEMPERATURE_ANALYSIS)
    if reply and len(reply.strip()) > 10:
        return reply.strip()
    if missing:
        return (
            f"You match {pct}% of the key requirements in this job description. Strengthening "
            f"{', '.join(missing[:3])} would significantly improve your fit for this role."
        )
    return f"You match {pct}% of the key requirements — a strong fit for this job description."


def analyze(resume_text, job_description, role):
    """Compare a resume against a pasted job description and score the keyword match."""
    job_keywords = _extract_keywords(job_description)
    resume_keywords_lower = {k.lower() for k in _extract_keywords(resume_text)}

    matched = [k for k in job_keywords if k.lower() in resume_keywords_lower]
    missing = [k for k in job_keywords if k.lower() not in resume_keywords_lower]
    total = len(job_keywords)
    pct = round((len(matched) / total) * 100) if total else 0
    label, badge = _verdict(pct)
    summary = _ai_summary(role, matched, missing, pct)

    return {
        "match_percent": pct,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "label": label,
        "badge": badge,
        "summary": summary,
        "total_keywords_found": total,
    }