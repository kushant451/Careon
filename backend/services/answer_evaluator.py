from ai_engine import llm_client, prompt_templates
from config.llm_config import LLM_TEMPERATURE_EVAL
from utils.helpers import safe_json_loads
from utils.logger import get_logger

logger = get_logger(__name__)

def evaluate(question, answer, role, keywords=None):
    prompt   = prompt_templates.answer_evaluation_prompt(role, question, answer)
    ai_reply = llm_client.chat(prompt, temperature=LLM_TEMPERATURE_EVAL)
    if ai_reply:
        parsed = safe_json_loads(ai_reply)
        if isinstance(parsed, dict) and "score" in parsed:
            parsed["score"] = max(0, min(10, int(parsed["score"])))
            return parsed
    return _rule_based(answer, keywords or [])

def _rule_based(answer, keywords):
    words   = answer.strip().split()
    wc      = len(words)
    matched = [k for k in keywords if k.lower() in answer.lower()]
    score   = max(0, min(10, round(min(5.0, wc/12) + (min(5.0, len(matched)*1.5) if keywords else (3.0 if wc>20 else 1.0)))))
    strengths, improvements = [], []
    if wc >= 30: strengths.append("Clear and reasonably detailed explanation")
    else:        improvements.append("Elaborate more — aim for at least 3–4 sentences")
    if matched:  strengths.append("Covered key concepts: " + ", ".join(matched[:3]))
    else:        improvements.append("Mention more specific technical terms")
    if not strengths:    strengths.append("Attempted a relevant answer")
    if not improvements: improvements.append("Add a real-world example to strengthen the answer")
    return {
        "score": score, "strengths": strengths, "improvements": improvements,
        "feedback": ("Your answer covers the basics. "
                     + ("Good use of relevant terminology. " if matched else "Include more specific terms. ")
                     + "Structure: brief explanation → example → takeaway.")
    }