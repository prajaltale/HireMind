"""Google Gemini LLM service for resume feedback and interview (Gemini 1.5 Flash)."""

import json
import logging
import re
from typing import Dict, List

from backend import config
from backend.services import local_ai

logger = logging.getLogger(__name__)

MODEL_ID = "gemini-1.5-flash"


def _get_client():
    """Lazy init Gemini client."""
    import google.generativeai as genai

    api_key = (getattr(config, "GEMINI_API_KEY", "") or "").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(MODEL_ID)


def _extract_json(text: str) -> str:
    """Extract JSON string from model output (handles fenced blocks)."""
    raw = (text or "").strip()
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    return (json_match.group(1).strip() if json_match else raw)


def get_resume_feedback(resume_text: str, job_description: str) -> Dict:
    """Resume feedback with Gemini, falling back to local heuristic if needed."""
    try:
        client = _get_client()
        prompt = f"""You are an expert HR evaluator. Analyze this resume against the given Job Description.

JOB DESCRIPTION:
{job_description[:4000]}

RESUME TEXT:
{resume_text[:8000]}

Respond in valid JSON only, with exactly these keys (no extra text):
- "strengths": list of 3-5 resume strengths (short strings)
- "weaknesses": list of 2-4 weaknesses or gaps (short strings)
- "suggestions": list of 3-5 actionable improvement suggestions (short strings)
- "recommendation": one short sentence: hiring recommendation (e.g. "Recommend for interview" or "Suggest improvements before interview")
"""
        response = client.generate_content(prompt)
        return json.loads(_extract_json(getattr(response, "text", "")))
    except Exception as exc:  # noqa: BLE001
        logger.warning("Gemini resume_feedback failed, using local fallback: %s", exc)
        return local_ai.get_resume_feedback(resume_text, job_description)


def generate_interview_questions(
    resume_text: str, job_description: str, count: int = 5
) -> List[str]:
    """Interview questions with Gemini, falling back to local heuristic if needed."""
    try:
        client = _get_client()
        prompt = f"""You are an expert interviewer. Based on the resume and job description, generate exactly {count} short interview questions.
One question per line. Mix: technical skills, experience, scenario-based. Keep each question under 2 lines.

JOB DESCRIPTION (excerpt):
{job_description[:2500]}

RESUME (excerpt):
{resume_text[:4000]}

Output only the questions, one per line, no numbering or bullets."""
        response = client.generate_content(prompt)
        lines = [
            q.strip()
            for q in (getattr(response, "text", "") or "").strip().split("\n")
            if q.strip()
        ]
        cleaned: List[str] = []
        for line in lines:
            line = re.sub(r"^[\d\.\)\-\*]+\s*", "", line).strip()
            if line:
                cleaned.append(line)
            if len(cleaned) >= count:
                break
        if cleaned:
            return cleaned[:count]
        raise RuntimeError("Gemini returned no questions")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Gemini questions failed, using local fallback: %s", exc)
        return local_ai.generate_interview_questions(resume_text, job_description, count)


def evaluate_answer(
    question: str,
    answer_text: str,
    resume_text: str,
    job_description: str,
) -> Dict:
    """Answer evaluation with Gemini, falling back to local heuristic if needed."""
    try:
        client = _get_client()
        prompt = f"""You are an interview evaluator. Score the candidate's answer.

QUESTION: {question}

CANDIDATE'S ANSWER: {answer_text}

Context - Job Description (excerpt): {job_description[:1500]}
Context - Resume (excerpt): {resume_text[:2000]}

Respond in valid JSON only, with exactly these keys:
- "score": number from 1 to 10 (integer)
- "strengths": list of 1-3 short points (what was good)
- "weaknesses": list of 1-3 short points (what could improve)
- "suggestions": list of 1-2 short actionable suggestions
"""
        response = client.generate_content(prompt)
        data = json.loads(_extract_json(getattr(response, "text", "")))
        if "score" in data:
            data["score"] = max(1, min(10, int(data["score"])))
        return data
    except Exception as exc:  # noqa: BLE001
        logger.warning("Gemini evaluate_answer failed, using local fallback: %s", exc)
        return local_ai.evaluate_answer(
            question=question,
            answer_text=answer_text,
            resume_text=resume_text,
            job_description=job_description,
        )

