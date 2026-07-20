import re, json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
with open(DATA_DIR / "skills_data.json", encoding="utf-8") as f:
    SKILLS_DATA = json.load(f)

SECTION_PATTERNS = {
    "Contact Information": r"(email|phone|linkedin|github|contact)",
    "Summary/Objective":   r"(summary|objective|profile|about)",
    "Skills":              r"(skills|technical skills|technologies|tech stack)",
    "Work Experience":     r"(experience|employment|work history|internship|intern)",
    "Education":           r"(education|academic|qualification|degree|b\.?tech)",
    "Projects":            r"(project|projects|project experience)",
}

def detect_sections(text):
    lower = text.lower()
    return {s: bool(re.search(p, lower)) for s, p in SECTION_PATTERNS.items()}

def extract_found_skills(text, keyword_list):
    lower = text.lower()
    return [kw for kw in keyword_list
            if re.search(r"\b" + re.escape(kw.lower()) + r"\b", lower)]

def compute_score(sections, found, total_keywords):
    section_score = (sum(sections.values()) / len(sections)) * 100
    keyword_score = (len(found) / total_keywords * 100) if total_keywords else 100
    return max(0, min(100, round(0.4 * section_score + 0.6 * keyword_score)))

def score_label(score):
    if score >= 85: return "Excellent score"
    if score >= 70: return "Good score"
    if score >= 50: return "Needs improvement"
    return "Poor score"

def generate_suggestions(sections, missing):
    tips = []
    if not sections.get("Summary/Objective"):
        tips.append("Add a 2–3 sentence Summary or Objective at the top")
    if not sections.get("Projects"):
        tips.append("Include a Projects section with measurable outcomes")
    if missing:
        tips.append("Add missing keywords: " + ", ".join(missing[:6]))
    tips.append("Use strong action verbs: built, designed, optimised, deployed")
    tips.append("Quantify achievements — add numbers and percentages")
    tips.append("Keep formatting simple: no tables, columns, or images")
    return tips

def run(text, role):
    keyword_list = SKILLS_DATA.get(role, list(SKILLS_DATA.values())[0])
    sections     = detect_sections(text)
    found        = extract_found_skills(text, keyword_list)
    missing      = [k for k in keyword_list if k not in found]
    score        = compute_score(sections, found, len(keyword_list))
    return {
        "sections": sections, "found_skills": found, "missing_skills": missing,
        "ats_score": score, "score_label": score_label(score),
        "suggestions": generate_suggestions(sections, missing),
    }