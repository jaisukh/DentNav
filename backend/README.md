# DentNav backend

FastAPI service for questionnaire delivery, OpenAI-powered pathway analysis, and Google OAuth user upsert.

## Stack

- Python 3.12+, [uv](https://docs.astral.sh/uv/)
- FastAPI + Uvicorn
- SQLAlchemy 2 (async) + asyncpg
- Alembic migrations (sync URL derived from `DATABASE_URL` by stripping `+asyncpg`)
- OpenAI (JSON mode) for analysis
- Optional S3 for questionnaire JSON; otherwise `data/questionnaire.v1.json`

## Setup

```bash
cd backend
uv sync --all-extras
cp .env.example .env
# edit .env — set DATABASE_URL, OPENAI_API_KEY, OAuth vars as needed
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment

See `.env.example` for all variables.

## API

See repository root `API_CONTRACT.md` for shapes consumed by the frontend.

## Tests & lint

```bash
uv run ruff check app tests
uv run pytest
```