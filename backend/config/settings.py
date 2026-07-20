import os
from dotenv import load_dotenv
load_dotenv()

def _get(key, default=""):
    return os.getenv(key, default)

SECRET_KEY         = _get("SECRET_KEY",     "dev-secret")
MONGO_URI          = _get("MONGO_URI",      "mongodb://localhost:27017")
MONGO_DB_NAME      = _get("MONGO_DB_NAME",  "ai_interview_prep")
OPENAI_API_KEY     = _get("OPENAI_API_KEY", "").strip()
USE_AI             = bool(OPENAI_API_KEY)

BASE_DIR           = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER      = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx"}

ROLES = [
    "Software Engineer",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "Data Analyst",
]
DIFFICULTY_LEVELS = ["All Levels", "Easy", "Medium", "Hard"]