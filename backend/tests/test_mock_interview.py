import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("OPENAI_API_KEY", "")

from services.question_generator import generate_generic, generate_personalized
from services.answer_evaluator import _rule_based
from services.report_generator import build, _empty_report

def test_generic_count():
    qs = generate_generic("Software Engineer", "All Levels", 5)
    assert 1 <= len(qs) <= 5

def test_generic_structure():
    for q in generate_generic("Software Engineer", "Easy", 3):
        assert "question" in q and "difficulty" in q

def test_personalized():
    qs = generate_personalized("Software Engineer", ["Python","Docker"], ["Chat app"], 3)
    assert len(qs) >= 1

def test_rule_based_score_range():
    r = _rule_based("Normalization reduces redundancy in databases.", ["normalization","databases"])
    assert 0 <= r["score"] <= 10

def test_rule_based_keys():
    r = _rule_based("test answer", [])
    assert all(k in r for k in ["score","strengths","improvements","feedback"])

def test_empty_report():
    r = _empty_report()
    assert r["overall_score"] == 0 and r["attempted"] == 0

def test_build_report():
    iv = {
        "role":"SE","personalized":False,
        "questions":[{"question":"Q1","category":"Technical","difficulty":"Easy","keywords":[]}],
        "answers":{"0":"ans"},
        "evaluations":{"0":{"score":8,"strengths":[],"improvements":[],"feedback":"Good"}},
    }
    r = build(iv)
    assert r["overall_score"] == 8.0 and r["correct"] == 1