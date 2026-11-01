import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.config.settings import SECRET_KEY, ALGORITHM
from app.models.database import User, Analysis, get_db
from app.models.schema import AnalysisCreate, AnalysisResponse

router = APIRouter()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT token."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


@router.post("/analyses", response_model=AnalysisResponse)
def save_analysis(
    analysis: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save an analysis result to the database for the authenticated user."""
    db_analysis = Analysis(
        user_id=current_user.id,
        company_name=analysis.company_name or "",
        job_title=analysis.job_title,
        match_score=analysis.match_score,
        skills_score=analysis.skills_score,
        resume_skills=json.dumps(analysis.resume_skills),
        missing_skills=json.dumps(analysis.missing_skills),
        strengths=json.dumps(analysis.strengths),
        suggestions=json.dumps(analysis.suggestions),
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return _analysis_to_response(db_analysis)


@router.get("/analyses", response_model=List[AnalysisResponse])
def list_analyses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
):
    """List the current user's past analyses (newest first)."""
    analyses = (
        db.query(Analysis)
        .filter(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_analysis_to_response(a) for a in analyses]


@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single analysis by ID (requires ownership)."""
    analysis = (
        db.query(Analysis)
        .filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return _analysis_to_response(analysis)


@router.delete("/analyses/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an analysis by ID (requires ownership)."""
    analysis = (
        db.query(Analysis)
        .filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    db.delete(analysis)
    db.commit()
    return {"message": "Analysis deleted successfully"}


def _analysis_to_response(analysis: Analysis) -> AnalysisResponse:
    """Convert an Analysis DB model to AnalysisResponse schema safely."""
    def _parse_list(field_value: Optional[str]) -> List[str]:
        if not field_value:
            return []
        try:
            val = json.loads(field_value)
            return val if isinstance(val, list) else [str(val)]
        except Exception:
            try:
                import ast
                val = ast.literal_eval(field_value)
                return val if isinstance(val, list) else [str(val)]
            except Exception:
                return [field_value]

    return AnalysisResponse(
        id=analysis.id,
        company_name=analysis.company_name,
        job_title=analysis.job_title,
        match_score=analysis.match_score,
        skills_score=analysis.skills_score,
        resume_skills=_parse_list(analysis.resume_skills),
        missing_skills=_parse_list(analysis.missing_skills),
        strengths=_parse_list(analysis.strengths),
        suggestions=_parse_list(analysis.suggestions),
        created_at=analysis.created_at,
    )
