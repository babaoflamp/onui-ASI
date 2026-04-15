# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Onui Korean** (오누이 한국어) is an AI-powered Korean language learning web platform. Backend: FastAPI (Python). Frontend: Jinja2 templates + Tailwind CSS. The app runs at port 9000 by default.

## Development Commands

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Dev server (hot reload)
source .venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port 9000 --reload

# Stop server
pkill -f uvicorn

# Run tests
python -m pytest
python -m pytest tests/unit          # unit tests only
python -m pytest tests/api           # API tests only
```

## Key Environment Variables (`.env`)

| Variable | Purpose | Default |
|---|---|---|
| `MODEL_BACKEND` | AI backend: `ollama`, `openai`, or `gemini` | `ollama` |
| `OLLAMA_URL` | Ollama server | `http://localhost:11434` |
| `OLLAMA_MODEL` | Model name | `exaone3.5:2.4b` |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | Gemini API | — |
| `GEMINI_MODEL` | Gemini model | `gemini-2.5-flash` |
| `OPENAI_API_KEY` | OpenAI (DALL-E, Whisper) | — |
| `MZTTS_API_URL` | Korean TTS service | `http://112.220.79.218:56014` |
| `SECRET_KEY` | Session signing | random at startup |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google OAuth | — |
| `ROMANIZE_MODE` | `force` (always romanize) or `prefer` (keep model output if valid) | `force` |
| `TTS_BACKEND` | `gemini`, `openai`, `google`, or `mztts` | `gemini` |
| `STT_BACKEND` | `openai`, `google`, `vosk`, or `local` | auto |

## Architecture

### Single-file Backend (`main.py`, ~7300 lines)

All FastAPI routes, middleware, and most business logic live in `main.py`. It is large by design — don't split it without strong motivation.

Key sections in `main.py`:
- **Lines 1–500**: imports, env config, AI client initialization
- **Lines 500–970**: TTS helpers (MzTTS, Gemini, Google, OpenAI), audio conversion utilities
- **Lines 970–2090**: SQLite DB init (`data/users.db`), auth helpers (PBKDF2 passwords, session tokens), app factory, middleware setup
- **Lines 2090+**: All route handlers (`@app.get/post/...`)

### Microservices in `backend/services/`

| Service | Purpose |
|---|---|
| `speechpro_service.py` | Pronunciation evaluation via external SpeechPro API |
| `fluencypro_service.py` | Writing fluency evaluation |
| `learning_progress_service.py` | Track per-user learning progress in SQLite |
| `krdict_service.py` | Korean dictionary lookup (KRDICT API) |
| `dalle_service.py` | Image generation (DALL-E / Gemini) |
| `analytics_service.py` | Usage analytics |

### Database

SQLite at `data/users.db`. Schema is created/migrated programmatically in `_init_user_db()` (main.py ~line 977). The DB is called at startup and uses `_ensure_*` helper functions to add columns/tables to existing DBs — no migration framework.

Tables: `users`, `word_scores`, `sentence_scores`, `attendance`, RAG document tables, LMS tables, admin logging tables.

### Session Auth

Cookie-based sessions using an in-memory `active_sessions` dict (token → user info). Token is a 64-char hex string stored in an `auth_token` cookie. Sessions expire after 24 hours. Google OAuth via `authlib`. Admin roles use `is_admin` flag + `role` field (`learner`, `instructor`, `system_admin`).

### Frontend

- **`templates/base.html`**: Master layout — navigation, i18n initialization, character popup. All pages extend this.
- **`templates/components/`**: Reusable Jinja2 partials.
- **`static/js/` and `static/css/`**: Feature-specific assets with kebab-case names matching their template (e.g., `word-puzzle.js` ↔ `word-puzzle.html`).
- Tailwind CSS is loaded via CDN (not compiled locally).
- JavaScript in templates is mostly inline; standalone JS files exist only for complex pages (word-puzzle, vocab-garden, etc.).

### Data Files (`data/`)

Static JSON datasets read at startup or on-demand:
- `sentences.json` — 35 sentences for listening/puzzle activities
- `vocabulary.json` — 72 vocabulary words (A1–B2)
- `pronunciation-words.json` — pronunciation practice words
- `folktales.json` — 10 Korean folktales
- `cultural-expressions.json` — 30 cultural expressions
- `tts_cache/` — pre-generated TTS audio files (`.bin` = audio, `.json` = metadata)

## Coding Conventions

- Python: 4-space indentation, snake_case for modules and functions.
- Templates: mirror the Tailwind utility patterns already in use; don't introduce new CSS frameworks.
- Static assets: kebab-case filenames; keep CSS/JS co-located by feature name.
- Commit style: `feat:`, `fix:`, `refactor:`, `chore:` prefixes with optional scope (e.g., `fix(ui): ...`).

## AI Backend Routing

The `MODEL_BACKEND` env var controls which LLM handles content generation:
- `ollama` → local EXAONE model via Ollama REST API
- `openai` → OpenAI GPT via `openai` SDK
- `gemini` → Gemini via `google-genai` SDK

TTS and STT have separate backend selectors (`TTS_BACKEND`, `STT_BACKEND`) and can differ from the main `MODEL_BACKEND`.
