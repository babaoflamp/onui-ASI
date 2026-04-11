# GEMINI.md

## Project Overview

This project, "Onui Korean," is a web-based platform designed for Korean language learners. It leverages a varietyso of AI technologies to provide an interactive and effective learning experience. The backend is built with Python using the FastAPI framework, and the frontend is rendered using Jinja2 templates.

The application features:

*   **Pronunciation Practice:** AI-powered pronunciation scoring and feedback.
*   **AI Learning Tools:** Personalized content generation and fluency testing.
*   **Interactive Activities:** Gamified learning experiences like word puzzles and quizzes.
*   **Cultural Content:** Folktales and cultural expressions to provide context for language learning.

## Building and Running

### 1. Environment Setup

It is recommended to use a Python virtual environment.

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the project root and add the necessary environment variables. See `.env.example` for a template. Key variables include:

*   `MODEL_BACKEND`: "ollama", "openai", or "gemini"
*   `OLLAMA_URL`: URL for the Ollama API
*   `OLLAMA_MODEL`: The Ollama model to use
*   `MZTTS_API_URL`: URL for the MzTTS API
*   `OPENAI_API_KEY`: Your OpenAI API key
*   `GEMINI_API_KEY`: Your Gemini API key
*   `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
*   `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret

### 3. Running the Application

To run the development server:

```bash
uvicorn main:app --reload
```

The application will be available at `http://localhost:8000`.

## Development Conventions

*   **Backend:** The backend is built with FastAPI. New features should be implemented as separate API endpoints and services.
*   **Frontend:** The frontend uses Jinja2 templates. UI components are located in the `templates/components` directory.
*   **Styling:** Tailwind CSS is used for styling.
*   **AI Services:** The application integrates with multiple AI services. The choice of service is determined by the `MODEL_BACKEND` environment variable.
*   **Database:** SQLite is used for the user database. The schema is defined and initialized in `main.py`.
*   **Dependencies:** Python dependencies are managed with `pip` and are listed in `requirements.txt`.
