"""Resume parsing service using pdfplumber."""
import re
import io
from typing import Optional

import pdfplumber


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract and clean text from PDF bytes."""
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_content)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    raw = "\n".join(text_parts) if text_parts else ""
    return clean_resume_text(raw)


def clean_resume_text(raw: str) -> str:
    """Normalize whitespace and remove noisy patterns."""
    if not raw:
        return ""
    # Collapse multiple spaces/newlines
    text = re.sub(r"\s+", " ", raw)
    # Remove common PDF artifacts
    text = re.sub(r"\x00", "", text)
    return text.strip()
