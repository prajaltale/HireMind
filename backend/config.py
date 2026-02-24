"""Application configuration."""
import os
import re
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (parent of backend/)
_project_root = Path(__file__).resolve().parent.parent
_env_path = _project_root / ".env"
load_dotenv(dotenv_path=_env_path)

GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()

# Fallback: read .env directly if dotenv didn't load (e.g. encoding/CWD issues)
if not GEMINI_API_KEY and _env_path.exists():
    try:
        raw = _env_path.read_text(encoding="utf-8-sig").strip()  # utf-8-sig strips BOM
        for line in raw.splitlines():
            line = line.strip()
            if line.startswith("#") or "GEMINI_API_KEY" not in line:
                continue
            match = re.match(r"GEMINI_API_KEY\s*=\s*(.*)", line)
            if match:
                GEMINI_API_KEY = (match.group(1).strip().strip("'\""))
                break
    except Exception:
        pass

# Last resort: use default key so the app works (prefer .env in production)
if not GEMINI_API_KEY:
    GEMINI_API_KEY = "AIzaSyCTmE5QvICMwkEtRyQWn7sxcAZ2o2IPxZI"
