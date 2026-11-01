import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "change-me")

# Base directory for backend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "resume_analyzer.db").replace("\\", "/")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# JWT Auth
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

# CORS allowed origins (comma-separated, e.g. "http://localhost:3000,https://your-app.vercel.app")
_cors_default = "http://localhost:3000,http://127.0.0.1:3000"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", _cors_default).split(",")]
