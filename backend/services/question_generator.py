import json, random
from pathlib import Path
from ai_engine import llm_client, prompt_templates
from config.llm_config import LLM_TEMPERATURE_CREATIVE
from utils.helpers import safe_json_loads
from utils.logger import get_logger

logger = get_logger(__name__)
DATA_DIR = Path(__file__).parent.parent / "data"
with open(DATA_DIR / "question_bank.json", encoding="utf-8") as f:
    QUESTION_BANK = json.load(f)

def _tag_ids(questions):
    for i, q in enumerate(questions):
        q.setdefault("id", i)
        q.setdefault("keywords", [])
    return questions

def _fallback_pool(role, difficulty):
    pool = QUESTION_BANK
    if difficulty != "All Levels":
        pool = [q for q in pool if q.get("difficulty") == difficulty]
    role_pool = [q for q in pool if role in q.get("roles",[]) or "All" in q.get("roles",[])]
    return role_pool if role_pool else pool

def generate_generic(role, difficulty, count):
    prompt   = prompt_templates.question_generation_prompt(role, difficulty, count)
    ai_reply = llm_client.chat(prompt, temperature=LLM_TEMPERATURE_CREATIVE)
    if ai_reply:
        parsed = safe_json_loads(ai_reply)
        if isinstance(parsed, list) and parsed:
            return _tag_ids(parsed[:count])
    pool   = _fallback_pool(role, difficulty)
    sample = random.sample(pool, min(count, len(pool)))
    return _tag_ids([{"question":q["question"],"category":q.get("category","Technical"),
                      "difficulty":q.get("difficulty","Medium"),"keywords":q.get("keywords",[])}
                     for q in sample])

def generate_personalized(role, found_skills, projects, count):
    prompt   = prompt_templates.personalized_question_prompt(role, found_skills, projects, count)
    ai_reply = llm_client.chat(prompt, temperature=LLM_TEMPERATURE_CREATIVE)
    if ai_reply:
        parsed = safe_json_loads(ai_reply)
        if isinstance(parsed, list) and parsed:
            return _tag_ids(parsed[:count])
    matched = [q for q in QUESTION_BANK
               if any(s.lower() in [k.lower() for k in q.get("keywords",[])] for s in found_skills)]
    pool   = matched if matched else _fallback_pool(role, "All Levels")
    sample = random.sample(pool, min(count, len(pool)))
    return _tag_ids([{"question":q["question"],"category":q.get("category","Technical"),
                      "difficulty":q.get("difficulty","Medium"),
                      "keywords":q.get("keywords",[]),"personalized":True}
                     for q in sample])