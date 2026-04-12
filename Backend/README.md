# Backend (FastAPI + Postgres + Prisma)

This service replaces the temporary Next.js route handlers and provides the API contract the frontend already expects.

## Stack

- FastAPI
- PostgreSQL
- Prisma ORM (`prisma-client-py`)

## Endpoints

- `GET /api/v1/questionnaire`
  - Returns questionnaire JSON for the frontend form.
  - Source: `AWS_S3_BUCKET` + `AWS_S3_QUESTIONNAIRE_KEY` (+ `AWS_REGION`).

- `GET /api/v1/analysis`
  - Returns analysis payload shape expected by `AnalysisView`.

- `POST /api/v1/analysis`
  - Placeholder for future LLM call; currently returns the same mock payload.

- `GET /api/v1/auth/google/login`
  - OAuth entrypoint.
  - Requires real Google OAuth credentials.

- `GET /api/v1/auth/google/callback`
  - Exchanges code for token (real mode) and fetches Google email.
  - Upserts user (`email`, `token`) into Postgres via Prisma.
  - Redirects to frontend `/home` (Hello World page).

## Required env vars

- API/runtime:
  - `DATABASE_URL`
  - `BACKEND_CORS_ORIGINS`
  - `FRONTEND_BASE_URL`
- S3:
  - `AWS_REGION`
  - `AWS_S3_BUCKET`
  - `AWS_S3_QUESTIONNAIRE_KEY`
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_SESSION_TOKEN` (optional, only for temporary credentials)
- Google OAuth:
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`
  - `GOOGLE_REDIRECT_URI` (must match Google console redirect URI)

## How to obtain the keys

### AWS (S3)

1. Go to [AWS Console](https://console.aws.amazon.com/) -> **IAM** -> **Users**.
2. Create a user (or use an existing service user) with programmatic access.
3. Attach least-privilege policy allowing `s3:GetObject` on your questionnaire object path.
4. Create access keys for that user:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
5. Find your bucket and object key in **S3**:
   - bucket name -> `AWS_S3_BUCKET`
   - object path (e.g. `configs/questionnaire.v1.json`) -> `AWS_S3_QUESTIONNAIRE_KEY`
6. Set region (bucket region) in `AWS_REGION`.

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Select project -> **APIs & Services**:
   - Configure **OAuth consent screen**.
   - Create **Credentials -> OAuth client ID -> Web application**.
3. Add Authorized redirect URI:
   - `http://localhost:8000/api/v1/auth/google/callback`
4. Copy values:
   - `Client ID` -> `GOOGLE_CLIENT_ID`
   - `Client secret` -> `GOOGLE_CLIENT_SECRET`
5. Set `GOOGLE_REDIRECT_URI` to exactly the same URI as above.

## Run locally

1. Create env file:
   - `cp Backend/.env.example Backend/.env`
2. Install dependencies:
   - `pip install -r Backend/requirements.txt`
3. Generate Prisma Python client:
   - `cd Backend`
   - `prisma generate`
4. Apply schema:
   - `prisma db push`
5. Start API:
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

## Run full stack with Docker (one command)

From repo root:

- `npm run dev:stack`

This brings up:

- Postgres on `localhost:5432`
- FastAPI backend on `localhost:8000`
- Next.js frontend on `localhost:3000`

Stop and remove containers + volume:

- `npm run dev:stack:down`

## DB GUI options

- **Prisma Studio** (`prisma studio`) for quick row-level inspection/editing.
- **pgAdmin** for SQL-first admin workflows.
- **TablePlus** (or DBeaver) for lightweight desktop browsing/querying.
