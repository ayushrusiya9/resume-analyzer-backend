import json
import logging
from google import genai
from app.config.settings import GEMINI_API_KEY

logger = logging.getLogger("ai_service")

# Initialize client if API key is provided
client = None
if GEMINI_API_KEY and GEMINI_API_KEY != "change-me":
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as err:
        logger.warning(f"Could not initialize Gemini client: {err}")

async def generate_ai_analysis(
    role: str,
    resume_skills: list[str],
    missing_skills: list[str],
    resume_text: str = "",
    job_description: str = ""
) -> tuple[list[str], list[str]]:
    """
    Generate AI analysis returning a tuple of (strengths, suggestions).
    Uses Gemini API async call without arbitrary sleeping.
    """
    resume_str = ", ".join(resume_skills) if resume_skills else "None explicitly detected"
    missing_str = ", ".join(missing_skills) if missing_skills else "No major missing skills"

    # Default fallback data
    fallback_strengths = [
        f"Demonstrates relevant background for {role}",
        f"Possesses core technical skills: {resume_str[:60]}...",
        "Solid foundational experience aligned with software domain"
    ]

    if not missing_skills:
        fallback_suggestions = [
            "Your resume strongly aligns with the target job requirements",
            "Ensure resume bullet points include quantifiable metrics (e.g. %, $)",
            "Highlight leadership and technical ownership in recent projects"
        ]
    else:
        fallback_suggestions = [
            f"Add key missing technologies: {missing_str[:60]}",
            f"Tailor project descriptions to highlight experience with {missing_skills[0]}",
            "Optimize resume header and summary for target ATS keywords",
            "Include practical project examples utilizing missing skills",
            "Align resume action verbs with job description requirements"
        ]

    if not client:
        return fallback_strengths, fallback_suggestions

    prompt = f"""
    You are an expert ATS (Applicant Tracking System) resume analyzer.
    Target Role: {role}
    Candidate Matched Skills: {resume_str}
    Missing Skills: {missing_str}
    Job Description Snippet: {job_description[:300]}

    Analyze the candidate's resume match and respond in JSON format ONLY:
    {{
      "strengths": [
        "Strength 1 (max 10 words)",
        "Strength 2 (max 10 words)",
        "Strength 3 (max 10 words)"
      ],
      "suggestions": [
        "Actionable tip 1 (max 12 words)",
        "Actionable tip 2 (max 12 words)",
        "Actionable tip 3 (max 12 words)",
        "Actionable tip 4 (max 12 words)"
      ]
    }}
    """

    try:
        # Use async call for Gemini model generate_content
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.text.strip()
        # Strip markdown code fencing if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        raw_text = raw_text.strip()

        data = json.loads(raw_text)
        strengths = data.get("strengths", fallback_strengths)[:3]
        suggestions = data.get("suggestions", fallback_suggestions)[:5]
        return strengths, suggestions

    except Exception as e:
        logger.error(f"Gemini AI Service Error: {e}")
        return fallback_strengths, fallback_suggestions

# Backward-compatibility alias
async def generate_suggestions(role: str, resume_skills: list[str], missing_skills: list[str]) -> list[str]:
    _, suggestions = await generate_ai_analysis(role, resume_skills, missing_skills)
    return suggestions