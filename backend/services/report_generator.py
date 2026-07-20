from utils.helpers import percent, stars

def build(interview, resume=None):
    questions   = interview.get("questions", [])
    answers     = interview.get("answers", {})
    evaluations = interview.get("evaluations", {})
    attempted   = len(answers)
    scores      = []
    for k in evaluations:
        ev = evaluations[k]
        if isinstance(ev, dict) and "score" in ev:
            scores.append(ev["score"])
    if not scores:
        return _empty_report()
    correct  = len([s for s in scores if s >= 6])
    overall  = round(sum(scores) / len(scores), 1)
    breakdown = {
        "Technical Knowledge": overall,
        "Communication":       max(0.0, round(overall - 0.3, 1)),
        "Problem Solving":     max(0.0, round(overall - 0.2, 1)),
        "Confidence":          max(0.0, round(overall - 0.1, 1)),
    }
    if overall >= 8.5:   label, summary = "Outstanding", "Exceptional performance! You're ready for real interviews."
    elif overall >= 7.0: label, summary = "Good Performance", "Good job. Focus on adding real-world examples."
    elif overall >= 5.0: label, summary = "Average", "Decent attempt. Revisit core concepts and practice more."
    else:                label, summary = "Needs Work", "Review fundamentals, practice regularly, focus on structure."
    ats_score = resume.get("ats_score", 0) if resume else 0
    return {
        "overall_score": overall, "performance_label": label,
        "stars": stars(overall), "total_questions": len(questions),
        "attempted": attempted, "correct": correct,
        "accuracy": percent(correct, attempted), "breakdown": breakdown,
        "summary": summary, "ats_score": ats_score,
        "resume_score": round(ats_score / 10, 1),
        "personalized": interview.get("personalized", False),
        "role": interview.get("role", ""),
    }

def _empty_report():
    return {
        "overall_score": 0, "performance_label": "No Data", "stars": "☆☆☆☆☆",
        "total_questions": 0, "attempted": 0, "correct": 0, "accuracy": 0,
        "breakdown": {"Technical Knowledge":0,"Communication":0,"Problem Solving":0,"Confidence":0},
        "summary": "No answers submitted. Complete a mock interview to see your report.",
        "ats_score": 0, "resume_score": 0, "personalized": False, "role": "",
    }