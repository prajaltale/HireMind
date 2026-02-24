"""ATS score and Job Description matching engine."""
import re
from typing import List, Tuple

# Common stopwords to exclude from keyword matching
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
    "be", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "must", "shall", "can", "need",
    "this", "that", "these", "those", "it", "its", "i", "we", "you",
    "they", "he", "she", "his", "her", "their", "my", "our", "your",
}


def tokenize_and_normalize(text: str) -> List[str]:
    """Extract lowercase alphanumeric tokens, excluding stopwords."""
    if not text:
        return []
    # Keep words (letters, numbers, allow dots in acronyms)
    tokens = re.findall(r"[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*", text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def extract_keywords_from_jd(jd: str, max_keywords: int = 80) -> List[str]:
    """Extract important keywords from job description."""
    tokens = tokenize_and_normalize(jd)
    # Simple frequency-based importance (could use TF-IDF later)
    from collections import Counter
    counts = Counter(tokens)
    return [w for w, _ in counts.most_common(max_keywords)]


def compute_ats_score(resume_text: str, job_description: str) -> Tuple[int, List[str], List[str]]:
    """
    Compare resume with JD and return:
    - ATS score (0-100)
    - List of matched skills/keywords
    - List of missing skills/keywords
    """
    resume_tokens = set(tokenize_and_normalize(resume_text))
    jd_keywords = extract_keywords_from_jd(job_description)
    if not jd_keywords:
        return 0, [], []

    matched = [k for k in jd_keywords if k in resume_tokens]
    missing = [k for k in jd_keywords if k not in resume_tokens]

    score = min(100, int(100 * len(matched) / len(jd_keywords)))
    return score, matched, missing
