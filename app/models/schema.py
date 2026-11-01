import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

# Pydantic models for resume analysis request and response schemas
class ResumeRequest(BaseModel):
    company_name: Optional[str] = ""
    job_title: str
    job_description: str


class ResumeResponse(BaseModel):
    company_name: Optional[str] = Field(default="", description="Target company name")
    job_title: str = Field(default="", description="Target job title")
    match_score: float = Field(..., description="Overall ATS Score out of 100")
    skills_score: float = Field(..., description="Percentage of required skills matched")
    resume_skills: List[str] = Field(default_factory=list, description="Skills detected in the resume")
    missing_skills: List[str] = Field(default_factory=list, description="Skills required in JD but missing in resume")
    strengths: List[str] = Field(default_factory=list, description="Key candidate strengths identified by AI")
    suggestions: List[str] = Field(default_factory=list, description="Actionable recommendations to improve ATS match")


# Auth schemas
class UserRegisterRequest(BaseModel):
    email: str = Field(..., min_length=3, description="User email address")
    password: str = Field(..., min_length=6, description="User password (min 6 chars)")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Invalid email format")
        return v


class UserLoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


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
