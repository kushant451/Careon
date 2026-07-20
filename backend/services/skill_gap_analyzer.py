import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
with open(DATA_DIR / "skills_data.json", encoding="utf-8") as f:
    SKILLS_DATA = json.load(f)

LEARNING_RESOURCES = {
    "Docker":         "https://docs.docker.com/get-started/",
    "Kubernetes":     "https://kubernetes.io/docs/tutorials/",
    "AWS":            "https://aws.amazon.com/training/",
    "CI/CD":          "https://www.atlassian.com/continuous-delivery",
    "System Design":  "https://github.com/donnemartin/system-design-primer",
    "React":          "https://react.dev/learn",
    "Node.js":        "https://nodejs.org/en/learn",
    "Machine Learning":"https://www.coursera.org/learn/machine-learning",
    "SQL":            "https://www.sqlzoo.net/",
    "Git":            "https://learngitbranching.js.org/",
}

HIGH_PRIORITY = {
    "Software Engineer":   ["Docker","System Design","CI/CD","AWS"],
    "Backend Developer":   ["Docker","Kubernetes","Redis","System Design"],
    "Frontend Developer":  ["React","TypeScript","Testing"],
    "Full Stack Developer":["React","Node.js","Docker","SQL"],
    "Data Analyst":        ["SQL","Machine Learning","Python","Tableau"],
}

def analyse(role, found_skills, missing_skills):
    total    = len(SKILLS_DATA.get(role, []))
    coverage = round((len(found_skills) / total) * 100) if total else 100
    hp       = HIGH_PRIORITY.get(role, [])
    gaps = [{
        "skill":    skill,
        "priority": "High" if skill in hp else "Medium",
        "resource": LEARNING_RESOURCES.get(
            skill, "https://www.google.com/search?q=learn+" + skill.replace(" ", "+"))
    } for skill in missing_skills]
    return {"coverage_percent": coverage, "gaps": gaps, "ready_to_apply": coverage >= 70}