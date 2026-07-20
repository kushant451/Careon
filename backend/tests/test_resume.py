import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ats_checker import detect_sections, extract_found_skills
from services import resume_analyzer

RESUME = """
John Doe  john@email.com
SUMMARY: B.Tech student with Python and SQL skills.
SKILLS: Python, SQL, Machine Learning, Pandas
EDUCATION: B.Tech CS 2024
PROJECTS: Sales Dashboard, Sentiment Analysis
"""

def test_sections_found():
    s = detect_sections(RESUME)
    assert s["Skills"] and s["Education"] and s["Projects"]

def test_top_skills_order():
    top = resume_analyzer.extract_top_skills(["Python","SQL"], "Python Python Python SQL")
    assert top[0] == "Python"

def test_strengths_not_empty():
    s = detect_sections(RESUME)
    f = extract_found_skills(RESUME, ["Python","SQL"])
    assert len(resume_analyzer.get_strengths(s, f, 300)) >= 1

def test_project_names():
    projects = resume_analyzer.extract_project_names(RESUME)
    assert len(projects) >= 1