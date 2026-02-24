# HireMind – AI Voice Interview & Resume Evaluation

AI-powered web platform for **resume parsing**, **ATS scoring**, **JD matching**, **AI resume feedback**, and **voice-based mock interviews** with instant evaluation.

## Features

- **Resume upload & parsing** – PDF upload, text extraction, and cleaning
- **ATS score & JD matching** – Compare resume with job description, keyword match, score 0–100, skill gap and improvement areas
- **AI resume feedback** – Google Gemini–powered strengths, weaknesses, suggestions, and hiring recommendation
- **Voice interview** – Personalized questions (TTS), voice answers (STT), AI evaluation (score, strengths, weaknesses, suggestions) and optional voice feedback

## Tech Stack

- **Backend:** FastAPI (Python)
- **AI:** Google Gemini API
- **Resume parsing:** pdfplumber
- **Voice:** Browser Web Speech API (Speech-to-Text, Text-to-Speech)
- **Frontend:** HTML, CSS, JavaScript

## Setup

1. **Clone / open project** and create a virtual environment:

   ```bash
   cd "e:\Cusrsor\Hire MInd"
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Gemini API key:**

   - Copy `.env.example` to `.env`
   - Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Set `GEMINI_API_KEY=your_key` in `.env`

4. **Run the app:**

   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Open in browser:**  
   http://localhost:8000

## Usage

1. **Upload resume** – PDF only; text is extracted automatically.
2. **Paste job description** in the text area.
3. **Calculate ATS score** – View score, matched keywords, and missing skills.
4. **Get AI feedback** – View strengths, weaknesses, suggestions, and recommendation.
5. **Start voice interview** – Generate questions, use “Speak question” (TTS), “Record answer” (STT), then “Evaluate answer” for score and feedback. Move to next question and repeat.

## API Docs

- Swagger UI: http://localhost:8000/docs  
- ReDoc: http://localhost:8000/redoc  

## Project Structure

```
Hire MInd/
├── backend/
│   ├── main.py           # FastAPI app & routes
│   ├── config.py         # Env config (e.g. GEMINI_API_KEY)
│   └── services/
│       ├── resume_parser.py   # PDF text extraction
│       ├── ats_engine.py      # ATS score & JD matching
│       └── gemini_service.py  # Resume feedback, questions, answer evaluation
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── requirements.txt
├── .env.example
└── README.md
```

## Notes

- **Speech recognition** works in Chrome/Edge (and other browsers that support Web Speech API). Use HTTPS or localhost for best support.
- **Gemini API** is required for resume feedback, question generation, and answer evaluation; ensure `.env` is set and the key has quota.
