# SchemeMate — AI-Driven Scheme Matching for Marginalized Entrepreneurs

A hackathon-ready MVP implementing:

- User registration/login with JWT
- Citizen profile
- Document upload + OCR assistance
- Structured government-scheme knowledge base
- Rule-based eligibility engine
- Evidence-based eligibility panel
- Application Readiness / Failure Prevention
- Financial what-if simulator
- Authorized channel-partner routing
- Application checklist + tracking
- Multilingual UI foundation
- AI semantic matching hook
- Security basics

## Stack

Frontend: React + Vite + Axios + React Router + CSS
Backend: FastAPI + MongoDB + JWT + bcrypt
OCR: Tesseract via pytesseract (optional; graceful fallback)
AI matching: optional OpenAI-compatible endpoint; deterministic keyword matching works without it.

## Important

The bundled scheme records are DEMO records for development. Before an SIH submission/demo claiming official scheme facts, replace/verify them against authoritative government sources and maintain `source_url` and `last_verified`.

## Run

### Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

MongoDB must be running locally or set MONGODB_URI in `.env`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

Default API:
`http://localhost:8000/api`

## Demo account

Register a new account from the UI. The application has no hard-coded demo password.

## Optional OCR

Install Tesseract OCR separately and ensure `tesseract` is on PATH. If unavailable, the upload still works and the API reports OCR as unavailable.

## Optional LLM matching

Set:
- `AI_ENABLED=true`
- `OPENAI_API_KEY=...`
- `OPENAI_BASE_URL=https://api.openai.com/v1`
- `OPENAI_MODEL=...`

The application remains usable without an LLM.
