# AI Tutor for Adaptive E-Learning

An MVP scaffold for an adaptive e-learning platform that combines adaptive quizzes, weak-topic detection, knowledge-graph-guided learning paths, personalized recommendations, an AI tutor API, and student analytics.

## Stack

- Frontend: Next.js
- Backend: FastAPI
- Adaptive logic: Python service layer
- Data layer: in-memory starter dataset designed to be replaced by PostgreSQL or MongoDB

## Structure

```text
backend/
  app/
    main.py
    data.py
    schemas.py
    services/
  requirements.txt
  tests/
frontend/
  app/
  lib/
  package.json
```

## Implemented MVP Features

- Adaptive learning engine with mastery scoring, weak-topic detection, and difficulty recommendations
- Knowledge graph with prerequisite-aware learning path status
- Recommendation system for remediation and next-topic suggestions
- AI tutor endpoint ready to be swapped with an external LLM
- Dashboard API for student metrics and progress

## Local Run

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://127.0.0.1:8000` unless `NEXT_PUBLIC_API_BASE_URL` is set.

## Core API Endpoints

- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `GET /api/health`
- `GET /api/courses`
- `GET /api/students/{student_id}/dashboard`
- `GET /api/students/{student_id}/knowledge-graph`
- `GET /api/quizzes/next?student_id=...&course_id=...`
- `POST /api/quizzes/submit`
- `POST /api/tutor/ask`

## Demo Login

- `ananya@tutorflow.dev` / `demo123`
- `rahul@tutorflow.dev` / `demo123`

## Suggested Next Steps

1. Replace the in-memory store with PostgreSQL.
2. Add JWT auth and role-based access.
3. Integrate OpenAI, Gemini, or a local LLaMA endpoint for the tutor.
4. Persist quiz event streams for cohort analytics.
5. Add teacher and admin dashboards.
