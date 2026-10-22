import sys
import os

# Ensure backend root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config.settings import CORS_ORIGINS
from app.api.routes import router
from app.api.auth import router as auth_router
from app.api.analysis import router as analysis_router

app = FastAPI(title="AI Resume Analyzer API", version="1.0.0")

# CORS — restrict to your frontend domain(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rate limiting on public upload endpoint
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.get("/")
def home():
    return {"message": "AI Resume Analyzer & Job Matcher API is running!"}

# /analyze-resume stays PUBLIC — no auth required
app.include_router(router, prefix="/api/v1")

# Auth routes (optional, only for saving history)
app.include_router(auth_router, prefix="/api/v1/auth")

# Analysis history routes (requires authentication)
app.include_router(analysis_router, prefix="/api/v1")