from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from app.config.settings import DATABASE_URL

Base = declarative_base()

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    analyses = relationship("Analysis", back_populates="user")


class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # nullable = anonymous upload OK
    company_name = Column(String(255))
    job_title = Column(String(255), nullable=False)
    match_score = Column(Float, nullable=False)
    skills_score = Column(Float, nullable=False)
    resume_skills = Column(Text)  # JSON string
    missing_skills = Column(Text)  # JSON string
    strengths = Column(Text)  # JSON string
    suggestions = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="analyses")