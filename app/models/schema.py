from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# Pydantic models for request and response schemas
class ResumeRequest(BaseModel):
    company_name: Optional[str] = ""
    job_title: str
    job_description: str

# Pydantic model for response schema
class ResumeResponse(BaseModel):
    match_score: float = Field(..., description="Overall ATS Score out of 100")
    skills_score: float = Field(..., description="Percentage of required skills matched")
    resume_skills: List[str] = Field(default_factory=list, description="Skills detected in the resume")
    missing_skills: List[str] = Field(default_factory=list, description="Skills required in JD but missing in resume")
    strengths: List[str] = Field(default_factory=list, description="Key candidate strengths identified by AI")
    suggestions: List[str] = Field(default_factory=list, description="Actionable recommendations to improve ATS match")


# Analysis schemas for saving/history
class AnalysisCreate(BaseModel):
    company_name: Optional[str] = ""
    job_title: str
    match_score: float
    skills_score: float
    resume_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    id: int
    company_name: Optional[str] = None
    job_title: str
    match_score: float
    skills_score: float
    resume_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True

