from datetime import datetime, timezone

def resume_doc(session_id, filename, raw_text, role, sections,
               found_skills, missing_skills, ats_score, score_label,
               suggestions, strengths, weaknesses, top_skills, summary):
    return {
        "session_id": session_id, "filename": filename, "raw_text": raw_text,
        "role": role, "sections": sections, "found_skills": found_skills,
        "missing_skills": missing_skills, "ats_score": ats_score,
        "score_label": score_label, "suggestions": suggestions,
        "strengths": strengths, "weaknesses": weaknesses,
        "top_skills": top_skills, "summary": summary,
        "created_at": datetime.now(timezone.utc),
    }

def interview_doc(session_id, role, questions, personalized=False):
    return {
        "session_id": session_id, "role": role, "questions": questions,
        "personalized": personalized, "answers": {}, "evaluations": {},
        "current_index": 0, "status": "in_progress",
        "started_at": datetime.now(timezone.utc), "completed_at": None,
    }

def history_doc(session_id, role, ats_score, interview_score,
                total_questions, attempted, accuracy, breakdown, summary):
    return {
        "session_id": session_id, "role": role, "ats_score": ats_score,
        "interview_score": interview_score, "total_questions": total_questions,
        "attempted": attempted, "accuracy": accuracy, "breakdown": breakdown,
        "summary": summary, "created_at": datetime.now(timezone.utc),
    }

def career_recommendation_doc(session_id, role, top_matches, insight):
    return {
        "session_id": session_id, "role": role, "top_matches": top_matches,
        "insight": insight, "created_at": datetime.now(timezone.utc),
    }

def roadmap_doc(session_id, role, weeks, milestones, total_skills, generated_by_ai):
    return {
        "session_id": session_id, "role": role, "weeks": weeks,
        "milestones": milestones, "total_skills": total_skills,
        "generated_by_ai": generated_by_ai, "created_at": datetime.now(timezone.utc),
    }

def job_match_doc(session_id, role, job_description, match_percent,
                   matched_keywords, missing_keywords, summary):
    return {
        "session_id": session_id, "role": role, "job_description": job_description,
        "match_percent": match_percent, "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords, "summary": summary,
        "created_at": datetime.now(timezone.utc),
    }