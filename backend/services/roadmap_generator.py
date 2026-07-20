import json
from pathlib import Path
from ai_engine import llm_client, prompt_templates
from config.llm_config import LLM_TEMPERATURE_CREATIVE
from utils.helpers import safe_json_loads
from services.skill_gap_analyzer import LEARNING_RESOURCES

DATA_DIR = Path(__file__).parent.parent / "data"
with open(DATA_DIR / "skills_data.json", encoding="utf-8") as f:
    SKILLS_DATA = json.load(f)


def _resource_for(skill):
    return LEARNING_RESOURCES.get(
        skill, "https://www.google.com/search?q=learn+" + skill.replace(" ", "+")
    )


def _chunk(items, n):
    if not items:
        return [[] for _ in range(n)]
    k, m = divmod(len(items), n)
    return [items[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


def _fallback_roadmap(role, missing_skills, weeks):
    base = list(missing_skills) if missing_skills else list(SKILLS_DATA.get(role, []))
    if not base:
        base = ["Core Fundamentals", "Practice Projects", "Interview Prep"]
    groups = _chunk(base, weeks)
    milestones = []
    for i, group in enumerate(groups, start=1):
        if group:
            title = f"Week {i}: {', '.join(group[:2])}"
            tasks = [f"Study and practice {s}" for s in group] + [f"Build a mini project using {group[0]}"]
        else:
            title = f"Week {i}: Consolidation & Practice"
            tasks = ["Revise previous weeks' topics", "Build a small project combining learned skills",
                      "Take a mock interview to test progress"]
        milestones.append({
            "week": i,
            "title": title,
            "skills": group,
            "tasks": tasks,
            "resources": [{"skill": s, "url": _resource_for(s)} for s in group],
        })
    return milestones


def _ai_roadmap(role, missing_skills, weeks):
    prompt = prompt_templates.roadmap_prompt(role, missing_skills, weeks)
    reply = llm_client.chat(prompt, temperature=LLM_TEMPERATURE_CREATIVE)
    if not reply:
        return None
    parsed = safe_json_loads(reply)
    if not isinstance(parsed, list) or not parsed:
        return None
    result = []
    for i, item in enumerate(parsed[:weeks], start=1):
        item.setdefault("week", i)
        item.setdefault("skills", [])
        item.setdefault("tasks", [])
        item["resources"] = [{"skill": s, "url": _resource_for(s)} for s in item.get("skills", [])]
        result.append(item)
    return result


def generate(role, missing_skills, weeks=8):
    """Build a week-by-week learning roadmap to close the candidate's skill gaps."""
    weeks = max(2, min(int(weeks), 16))
    ai_result = _ai_roadmap(role, missing_skills, weeks)
    milestones = ai_result if ai_result else _fallback_roadmap(role, missing_skills, weeks)
    total_skills = sum(len(m.get("skills", [])) for m in milestones)
    return {
        "role": role,
        "weeks": weeks,
        "milestones": milestones,
        "total_skills": total_skills,
        "generated_by_ai": bool(ai_result),
    }