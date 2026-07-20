def question_generation_prompt(role, difficulty, count):
    level = ("mixing Easy, Medium and Hard" if difficulty == "All Levels"
             else f"at {difficulty} difficulty")
    return (
        f"Generate exactly {count} interview questions for a {role} role, {level}.\n"
        "Mix Technical, HR, and Project Based categories.\n"
        "Return ONLY a valid JSON array, no extra text, no markdown fences.\n"
        'Format: [{"question":"...","category":"Technical","difficulty":"Medium","keywords":["..."]}]'
    )

def personalized_question_prompt(role, skills, projects, count):
    skill_str   = ", ".join(skills[:20])  if skills   else "general programming"
    project_str = ", ".join(projects[:5]) if projects else "personal projects"
    return (
        f"You are an interviewer preparing personalized questions for a {role} candidate.\n"
        f"Their skills: {skill_str}.\nTheir projects: {project_str}.\n"
        f"Generate exactly {count} questions tailored to THEIR specific skills and projects.\n"
        "Return ONLY a valid JSON array, no extra text, no markdown fences.\n"
        'Format: [{"question":"...","category":"Technical","difficulty":"Medium","keywords":["..."]}]'
    )

def answer_evaluation_prompt(role, question, answer):
    return (
        f"You are an expert interviewer evaluating a {role} candidate.\n"
        f"Question: {question}\nCandidate's answer: {answer}\n\n"
        "Return ONLY a valid JSON object, no extra text.\n"
        '{"score":7,"strengths":["..."],"improvements":["..."],"feedback":"2-3 sentences"}'
    )

def resume_summary_prompt(resume_text, role):
    return (
        f"Analyse this resume for a {role} role in 2-3 sentences. "
        "Highlight the strongest asset and most important thing to fix.\n"
        f"Return ONLY plain text.\n\nResume:\n{resume_text[:3000]}"
    )

def career_recommendation_prompt(role, skills, top_path_title, top_path_skills):
    skill_str = ", ".join(skills[:20]) if skills else "general skills"
    return (
        f"A candidate currently targeting a {role} role has these skills: {skill_str}.\n"
        f"Their top recommended career path is {top_path_title}, which typically needs: "
        f"{', '.join(top_path_skills)}.\n"
        "In 2-3 sentences, explain why this path fits them and what to focus on next.\n"
        "Return ONLY plain text, no markdown."
    )

def roadmap_prompt(role, missing_skills, weeks):
    skills_str = ", ".join(missing_skills) if missing_skills else "core fundamentals for the role"
    return (
        f"Create a {weeks}-week learning roadmap for someone targeting a {role} role.\n"
        f"They need to learn: {skills_str}.\n"
        f"Return ONLY a valid JSON array of exactly {weeks} objects, no extra text, no markdown fences.\n"
        'Format: [{"week":1,"title":"...","skills":["..."],"tasks":["..."]}]'
    )

def job_match_prompt(role, matched, missing, pct):
    return (
        f"A candidate applying for a {role} role matches {pct}% of a job description's key skill keywords.\n"
        f"Matched keywords: {', '.join(matched) if matched else 'none'}.\n"
        f"Missing keywords: {', '.join(missing) if missing else 'none'}.\n"
        "In 2-3 sentences, give a fit summary and the single most important improvement to make.\n"
        "Return ONLY plain text, no markdown."
    )