import re
from ai_engine import llm_client, prompt_templates
from utils.text_cleaner import word_count
from config.llm_config import LLM_TEMPERATURE_ANALYSIS

def extract_top_skills(found_skills, text):
    lower = text.lower()
    scored = [(s, len(re.findall(r"\b" + re.escape(s.lower()) + r"\b", lower)))
              for s in found_skills]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [s for s, _ in scored[:8]]

def extract_project_names(text):
    lines, projects, in_proj = text.splitlines(), [], False
    for line in lines:
        s = line.strip()
        if re.search(r"\b(projects?)\b", s, re.IGNORECASE):
            in_proj = True; continue
        if in_proj and s:
            if re.search(r"\b(education|experience|skills|summary|contact)\b", s, re.IGNORECASE):
                break
            if len(s) > 5 and not s.startswith(("•", "-")):
                projects.append(s.split("|")[0].split("–")[0].strip())
    return projects[:5]

def get_strengths(sections, found_skills, wc):
    s = []
    if sections.get("Skills") and found_skills:
        s.append("Strong technical skills section with relevant keywords")
    if sections.get("Projects"):       s.append("Relevant project experience clearly shown")
    if sections.get("Education"):      s.append("Academic background well documented")
    if wc > 250:                       s.append("Well-detailed resume with sufficient content")
    if sections.get("Work Experience"):s.append("Work / internship experience included")
    if not s: s.append("Resume parsed successfully — add more sections to build strengths")
    return s

def get_weaknesses(sections, missing_skills, wc):
    w = []
    if not sections.get("Work Experience"):
        w.append("No work experience or internship section found")
    if missing_skills:
        w.append("Missing key tech keywords: " + ", ".join(missing_skills[:4]))
    if not sections.get("Summary/Objective"):
        w.append("No summary or objective section detected")
    if wc < 150:
        w.append("Resume is very short — add more detail to each section")
    if not w: w.append("No critical weaknesses — focus on filling keyword gaps")
    return w

def generate_summary(text, role):
    prompt   = prompt_templates.resume_summary_prompt(text, role)
    ai_reply = llm_client.chat(prompt, temperature=LLM_TEMPERATURE_ANALYSIS)
    if ai_reply and len(ai_reply.strip()) > 20:
        return ai_reply.strip()
    return ("Your resume covers the core sections. Strengthen it by adding measurable "
            "achievements and the cloud/DevOps keywords that match your target role.")

def run(text, role, found_skills, missing_skills, sections):
    wc        = word_count(text)
    top       = extract_top_skills(found_skills, text)
    projects  = extract_project_names(text)
    strengths = get_strengths(sections, found_skills, wc)
    weaknesses= get_weaknesses(sections, missing_skills, wc)
    summary   = generate_summary(text, role)
    total     = len(found_skills) + len(missing_skills)
    return {
        "strengths": strengths, "weaknesses": weaknesses,
        "top_skills": top, "projects": projects, "summary": summary,
        "word_count": wc,
        "overall_score": round(min(10.0, len(found_skills) / max(total, 1) * 10), 1),
    }