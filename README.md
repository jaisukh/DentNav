# DentNav monorepo

- **`frontend/`** — Next.js app (UI, calls the API via `NEXT_PUBLIC_BACKEND_URL`).
- **`backend/`** — FastAPI API: questionnaire, OpenAI analysis, Google OAuth, PostgreSQL via SQLAlchemy.

## Quick start (local)

1. Start Postgres (or use Docker Compose):

   ```bash
   docker compose up -d postgres
   ```

2. Backend:

   ```bash
   cd backend
   cp .env.example .env
   # set OPENAI_API_KEY, DATABASE_URL (port 15432 for compose), OAuth if testing login
   uv sync --all-extras
   uv run alembic upgrade head
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Frontend:

   ```bash
   cd frontend
   npm ci
   echo 'NEXT_PUBLIC_BACKEND_URL=http://localhost:8000' > .env.local
   npm run dev
   ```

   On Vercel (or similar), set the project **root directory** to `frontend` and configure `NEXT_PUBLIC_BACKEND_URL` to your deployed API URL.

## Full stack (Docker)

```bash
docker compose up --build
```

Frontend: http://localhost:3000 — Backend: http://localhost:8000

## API contract

See [`API_CONTRACT.md`](./API_CONTRACT.md) for request/response shapes expected by the frontend.
