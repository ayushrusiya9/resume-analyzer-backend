import os
from typing import Annotated, Optional
from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from app.models.schema import ResumeRequest, ResumeResponse
from app.services.docs_parser import extract_text
from app.services.skill_extractor import extract_skills
from app.services.matcher import calculate_overall_ats_score, missing_skills
from app.services.ai_service import generate_ai_analysis

router = APIRouter()

# Helper function to create ResumeRequest from form data
def get_resume_request(
    job_title: Annotated[str, Form()],
    job_description: Annotated[str, Form()],
    company_name: Annotated[Optional[str], Form()] = ""
) -> ResumeRequest:
    return ResumeRequest(
        company_name=company_name or "",
        job_title=job_title,
        job_description=job_description
    )

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}

# Endpoint to analyze resume
@router.post('/analyze-resume', response_model=ResumeResponse)
async def analyze_resume(
    resume: ResumeRequest = Depends(get_resume_request),
    resume_file: UploadFile = File(...),
):
    """Endpoint to analyze resume and match with job description (Supports PDF, DOCX, TXT)"""

    # Validate file extension
    filename = resume_file.filename or ""
    _, ext = os.path.splitext(filename.lower())

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext}'. Supported formats: PDF, DOCX, TXT, MD"
        )
    
    # Validate file size (limit to 5MB)
    contents = await resume_file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds the limit of 5MB.")

    # Validate required text fields
    if not resume.job_title.strip():
        raise HTTPException(status_code=400, detail="Job title cannot be empty.")

    if not resume.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    # Extract text using unified docs_parser
    try:
        text = extract_text(contents, filename=filename)
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Failed to parse resume file: {str(err)}")

    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract readable text from uploaded file.")

    # Extract skills
    extract_resume_skill = extract_skills(text)
    extract_jd_skill = extract_skills(resume.job_description)
    
    # Calculate scores & missing skills
    skills_score, overall_match_score = calculate_overall_ats_score(
        resume_skills=extract_resume_skill,
        jd_skills=extract_jd_skill,
        resume_text=text,
        job_title=resume.job_title
    )
    missing_skill_list = missing_skills(extract_resume_skill, extract_jd_skill)

    # Generate AI strengths & suggestions
    strengths, suggestions = await generate_ai_analysis(
        role=resume.job_title,
        resume_skills=extract_resume_skill,
        missing_skills=missing_skill_list,
        resume_text=text,
        job_description=resume.job_description
    )
    
    return ResumeResponse(
        match_score=overall_match_score,
        skills_score=skills_score,
        resume_skills=extract_resume_skill,
        missing_skills=missing_skill_list,
        strengths=strengths,
        suggestions=suggestions,
    )

