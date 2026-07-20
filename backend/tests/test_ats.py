import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ats_checker import detect_sections, extract_found_skills, compute_score, score_label

RESUME = """
John Doe  john@email.com  github.com/johndoe
SUMMARY: Passionate software engineer.
SKILLS: Python, Docker, SQL, REST API, Git, AWS, CI/CD
EDUCATION: B.Tech Computer Science 2024
WORK EXPERIENCE: Software Engineer Intern, TechCorp 2023
PROJECTS: E-commerce platform with React and Node.js
"""
KWS = ["Python","Docker","SQL","REST API","Git","AWS","CI/CD","Kubernetes","System Design"]

def test_all_sections(): assert all(detect_sections(RESUME).values())
def test_found_skills():
    found = extract_found_skills(RESUME, KWS)
    assert "Python" in found and "Docker" in found
    assert "Kubernetes" not in found
def test_score_range():
    s = detect_sections(RESUME)
    f = extract_found_skills(RESUME, KWS)
    assert 0 <= compute_score(s, f, len(KWS)) <= 100
def test_labels():
    assert score_label(90) == "Excellent score"
    assert score_label(75) == "Good score"
    assert score_label(55) == "Needs improvement"
    assert score_label(20) == "Poor score"