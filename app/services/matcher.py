def missing_skills(resume_skills: list[str], jd_skills: list[str]) -> list[str]:
    """Return list of skills required by job description but missing in candidate's resume."""
    resume_set = {s.lower() for s in resume_skills}
    missing = [skill for skill in jd_skills if skill.lower() not in resume_set]
    return sorted(missing)

def calculate_match_percentage(resume_skills: list[str], jd_skills: list[str]) -> float:
    """Calculate the percentage of matching skills between resume and job description."""
    if not jd_skills:
        return 100.0 if resume_skills else 50.0

    resume_set = {s.lower() for s in resume_skills}
    matching_count = sum(1 for s in jd_skills if s.lower() in resume_set)
    return round((matching_count / len(jd_skills)) * 100, 1)

def calculate_overall_ats_score(
    resume_skills: list[str],
    jd_skills: list[str],
    resume_text: str = "",
    job_title: str = ""
) -> tuple[float, float]:
    """Calculate both skills match score and overall weighted ATS score out of 100."""
    skills_score = calculate_match_percentage(resume_skills, jd_skills)

    # Base weight: 70% from skills match
    overall_score = skills_score * 0.70

    # Job title relevance bonus (up to 15%)
    if job_title and job_title.lower() in resume_text.lower():
        overall_score += 15.0
    elif any(word.lower() in resume_text.lower() for word in job_title.split() if len(word) > 3):
        overall_score += 8.0

    # Resume completeness bonus (up to 15%)
    word_count = len(resume_text.split())
    if 250 <= word_count <= 1200:
        overall_score += 15.0
    elif word_count > 100:
        overall_score += 8.0

    return round(skills_score, 1), round(min(overall_score, 100.0), 1)