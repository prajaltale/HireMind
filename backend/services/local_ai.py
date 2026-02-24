"""Local heuristic 'AI' fallback for resume feedback and interview.

Used automatically when Gemini API is unavailable (missing key, quota, etc.).
"""

import re
from typing import Dict, List


def _extract_keywords(text: str, limit: int = 20) -> List[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+\-#\.]{1,}", (text or "").lower())
    stop = {
        "and",
        "or",
        "the",
        "for",
        "with",
        "from",
        "this",
        "that",
        "using",
        "experience",
        "knowledge",
        "skills",
        "ability",
    }
    filt = [t for t in tokens if t not in stop and len(t) > 2]
    out: List[str] = []
    for t in filt:
        if t not in out:
            out.append(t)
        if len(out) >= limit:
            break
    return out


def get_resume_feedback(resume_text: str, job_description: str) -> Dict:
    """Heuristic resume feedback without external LLM."""
    resume_kw = set(_extract_keywords(resume_text, 40))
    jd_kw = set(_extract_keywords(job_description, 40))

    matched = sorted(resume_kw & jd_kw)
    missing = sorted(jd_kw - resume_kw)

    strengths: List[str] = []
    weaknesses: List[str] = []
    suggestions: List[str] = []

    if len(resume_text) > 1500:
        strengths.append("Resume provides good overall detail about experience.")
    else:
        weaknesses.append("Resume is quite short; add more detail on projects and impact.")
        suggestions.append("Add 2–3 bullet points per role describing your concrete achievements.")

    if matched:
        strengths.append(
            f"Resume mentions several key skills from the JD such as {', '.join(matched[:5])}."
        )
    else:
        weaknesses.append("Very little overlap between resume skills and job description keywords.")

    if missing:
        suggestions.append(
            "Highlight or add experience related to: " + ", ".join(missing[:6]) + "."
        )

    if "python" in resume_kw or "java" in resume_kw or "javascript" in resume_kw:
        strengths.append("Technical stack is clearly listed (programming languages / tools).")

    if "team" not in resume_text.lower() and "collaborat" not in resume_text.lower():
        suggestions.append("Mention collaboration, teamwork, or cross‑functional experience.")

    if not strengths:
        strengths.append("Resume structure is a good starting point.")
    if not weaknesses:
        weaknesses.append("Can be further tailored to the specific job description.")
    if not suggestions:
        suggestions.append("Refine bullet points to be more outcome‑focused (metrics, impact).")

    recommendation = (
        "Recommend for interview"
        if matched and len(matched) >= max(3, len(jd_kw) // 4)
        else "Suggest improvements before interview"
    )

    return {
        "strengths": strengths[:5],
        "weaknesses": weaknesses[:4],
        "suggestions": suggestions[:5],
        "recommendation": recommendation,
    }


def generate_interview_questions(
    resume_text: str, job_description: str, count: int = 5
) -> List[str]:
    """Generate simple, resume/JD‑aware interview questions."""
    kws = list(
        dict.fromkeys(
            _extract_keywords(job_description, 20) + _extract_keywords(resume_text, 20)
        )
    )

    questions: List[str] = []

    if kws:
        questions.append(
            f"Can you walk me through your most relevant experience with {kws[0]} for this role?"
        )
    if len(kws) > 1:
        questions.append(
            f"Tell me about a project where you used {kws[1]} and what the outcome was."
        )

    questions.extend(
        [
            "Describe a challenging problem you solved recently and how you approached it.",
            "How do you stay up to date with new tools, technologies or best practices?",
            "What attracts you to this specific role and company, and how do you see yourself adding value?",
        ]
    )

    return questions[: max(1, count)]


def evaluate_answer(
    question: str,
    answer_text: str,
    resume_text: str,
    job_description: str,
) -> Dict:
    """Very simple heuristic scoring of an answer."""
    text = (answer_text or "").strip()
    length = len(text.split())

    if length == 0:
        score = 1
    elif length < 20:
        score = 4
    elif length < 60:
        score = 7
    else:
        score = 9

    strengths: List[str] = []
    weaknesses: List[str] = []
    suggestions: List[str] = []

    if length >= 20:
        strengths.append("Provides a reasonably detailed explanation instead of a one‑line answer.")
    else:
        weaknesses.append("Answer is very brief; interviewer may need to ask many follow‑up questions.")
        suggestions.append("Expand your answers with context, actions you took, and concrete results.")

    jd_kw = set(_extract_keywords(job_description, 20))
    ans_kw = set(_extract_keywords(text, 20))
    overlap = jd_kw & ans_kw
    if overlap:
        strengths.append(
            "Connects the answer to job‑relevant skills such as "
            + ", ".join(sorted(overlap)[:4])
            + "."
        )
    else:
        suggestions.append("Try to mention skills and tools that are highlighted in the job description.")

    if "i" in text.lower() and ("we " in text.lower() or "team" in text.lower()):
        strengths.append("Balances talking about personal contribution with team collaboration.")

    strengths = strengths or ["Good starting point; can be refined with more structure and examples."]
    weaknesses = weaknesses or [
        "Could be more structured (Situation, Task, Action, Result) for clarity."
    ]
    suggestions = suggestions or [
        "Practice answering using a clear structure and include specific metrics where possible."
    ]

    return {
        "score": int(score),
        "strengths": strengths[:3],
        "weaknesses": weaknesses[:3],
        "suggestions": suggestions[:2],
    }

