"""
AI-Powered Voice Interview & Resume Evaluation - FastAPI Backend
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend import config as backend_config
from backend import auth as auth_service
from backend.services.resume_parser import extract_text_from_pdf
from backend.services.ats_engine import compute_ats_score
from backend.services.gemini_service import (
    get_resume_feedback,
    generate_interview_questions,
    evaluate_answer,
)

# ---------- Environment loading (GEMINI_API_KEY) ----------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

# Load variables from .env into process environment
load_dotenv(dotenv_path=ENV_PATH)

GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()

if not GEMINI_API_KEY:
    # Do not crash; Gemini calls will fall back to local heuristic logic.
    print(
        "[WARN] GEMINI_API_KEY is not set. "
        "Gemini features will use local fallback logic instead."
    )
else:
    # Propagate into backend.config so services that import it see the same value
    backend_config.GEMINI_API_KEY = GEMINI_API_KEY
    # Temporary debug print to confirm key presence (do not log the key itself)
    print(f"[DEBUG] GEMINI_API_KEY loaded in main: present={bool(GEMINI_API_KEY)}")

# Initialize auth DB
auth_service.init_db()

app = FastAPI(
    title="HireMind - AI Voice Interview & Resume Evaluation",
    description="Resume parsing, ATS scoring, AI feedback, and voice interview",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files (CSS, JS)
STATIC_DIR = Path(__file__).resolve().parent.parent / "frontend"
if STATIC_DIR.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ---------- Request/Response models ----------
class ParseResumeResponse(BaseModel):
    text: str
    success: bool = True


class JDInput(BaseModel):
    job_description: str


class ATSResponse(BaseModel):
    score: int
    matched_skills: list
    missing_skills: list
    improvement_areas: list  # same as missing_skills for UI


class EvaluateAnswerInput(BaseModel):
    question: str
    answer_text: str
    resume_text: str
    job_description: str


class AuthRegisterInput(BaseModel):
    name: str
    email: str
    password: str


class AuthLoginInput(BaseModel):
    email: str
    password: str


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


def get_current_user(authorization: str = Header(default="")):
    """Decode JWT from Authorization: Bearer <token> header."""
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1].strip()
    user = auth_service.get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


# ---------- API Routes ----------
@app.get("/")
async def root():
    """Serve frontend index."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "HireMind API", "docs": "/docs"}


# Redirect /index.html and serve static assets with correct path
@app.get("/index.html")
async def index_html():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    raise HTTPException(404)


@app.post("/api/auth/register", response_model=AuthTokenResponse)
async def register(payload: AuthRegisterInput):
    existing = auth_service.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    user = auth_service.create_user(
        email=payload.email, name=payload.name, password=payload.password
    )
    token = auth_service.create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.post("/api/auth/login", response_model=AuthTokenResponse)
async def login(payload: AuthLoginInput):
    user = auth_service.authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = auth_service.create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.post("/api/auth/google", response_model=AuthTokenResponse)
async def google_login(payload: dict):
    """Simplified Google sign-in endpoint.

    Expects: { "email": "...", "name": "..." }
    (In a production app you'd verify an ID token from Google here.)
    """
    email = (payload.get("email") or "").strip().lower()
    name = (payload.get("name") or "").strip()
    if not email:
        raise HTTPException(status_code=400, detail="email is required")
    user = auth_service.get_user_by_email(email)
    if not user:
        user = auth_service.create_user(email=email, name=name or email, password=None)
    token = auth_service.create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.get("/api/auth/me")
async def me(current_user: dict = Depends(get_current_user)):
    return current_user


@app.post("/api/parse-resume", response_model=ParseResumeResponse)
async def parse_resume(
    file: UploadFile = File(...), current_user: dict = Depends(get_current_user)
):
    """Upload PDF resume and extract text."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are allowed")
    content = await file.read()
    try:
        text = extract_text_from_pdf(content)
    except Exception as e:
        raise HTTPException(400, f"Failed to parse PDF: {str(e)}")
    return ParseResumeResponse(text=text)


@app.post("/api/ats-score", response_model=ATSResponse)
async def ats_score(payload: dict, current_user: dict = Depends(get_current_user)):
    """Compute ATS score from resume text and job description."""
    resume_text = payload.get("resume_text", "")
    job_description = payload.get("job_description", "")
    if not resume_text or not job_description:
        raise HTTPException(400, "resume_text and job_description are required")
    score, matched, missing = compute_ats_score(resume_text, job_description)
    return ATSResponse(
        score=score,
        matched_skills=matched,
        missing_skills=missing,
        improvement_areas=missing,
    )


@app.post("/api/resume-feedback")
async def resume_feedback(payload: dict, current_user: dict = Depends(get_current_user)):
    """Get AI resume feedback (strengths, weaknesses, suggestions, recommendation)."""
    resume_text = payload.get("resume_text", "")
    job_description = payload.get("job_description", "")
    if not resume_text or not job_description:
        raise HTTPException(400, "resume_text and job_description are required")
    try:
        return get_resume_feedback(resume_text, job_description)
    except ValueError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/interview/questions")
async def get_interview_questions(payload: dict, current_user: dict = Depends(get_current_user)):
    """Generate personalized interview questions from resume and JD."""
    resume_text = payload.get("resume_text", "")
    job_description = payload.get("job_description", "")
    count = int(payload.get("count", 5))
    if not resume_text or not job_description:
        raise HTTPException(400, "resume_text and job_description are required")
    try:
        questions = generate_interview_questions(resume_text, job_description, count=count)
        return {"questions": questions}
    except ValueError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/interview/evaluate")
async def evaluate_interview_answer(
    payload: EvaluateAnswerInput, current_user: dict = Depends(get_current_user)
):
    """Evaluate a single interview answer."""
    try:
        result = evaluate_answer(
            question=payload.question,
            answer_text=payload.answer_text,
            resume_text=payload.resume_text,
            job_description=payload.job_description,
        )
        return result
    except ValueError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/health")
async def health():
    # Quick runtime check to confirm which backend version is running.
    return {"status": "ok", "ai_mode": "gemini-1.5-flash"}
