# API Contract And Frontend Expectations

## Current Frontend Call Flow

1. Questionnaire page loads data via `fetchQuestionnaire()`.
2. Submit on questionnaire triggers `submitAnalysis({ answers })`.
3. Analysis page reads submit response from session storage, else `GET /analysis`.
4. Login button redirects browser to Google OAuth entrypoint URL.

## Endpoints consumed by frontend

### `GET /api/v1/questionnaire`

- **Expected by:** `QuestionnaireView`
- **Response shape:** `QuestionnaireDocument`
  - `version`, `lastUpdated`, `meta`
  - `degreesByCountry: Record<string, string[]>`
  - `questions: Question[]`
- **Source:** S3 (`AWS_S3_BUCKET` + `AWS_S3_QUESTIONNAIRE_KEY`) when configured; otherwise `backend/data/questionnaire.v1.json`.

### `POST /api/v1/analysis`

- **Expected by:** questionnaire submit
- **Request body:** `{ answers?: Record<string, unknown> }`
- **Validation:** Answers are validated against the loaded questionnaire (types, allowed options, dependencies). Invalid submissions return **422** with `{ "detail": [{ "loc": [...], "msg": "..." }] }`.
- **Response shape:** `AnalysisResultPayload`
  - `Country`, `degree`, `yearsOfExp`, `Performance`, `Body`
  - `Body` is an array of paragraph strings from OpenAI output (or mock fallback if the model omits body text).

### `GET /api/v1/analysis`

- **Expected by:** analysis page fallback load
- **Response shape:** same `AnalysisResultPayload`
- **Behavior:** returns `backend/data/analysis-mock.json` without calling OpenAI.

### `GET /api/v1/auth/google/login`

- **Expected by:** login button redirect
- **Behavior:** redirect to Google OAuth consent screen.

### `GET /api/v1/auth/google/callback`

- **Behavior:** exchange OAuth `code`, fetch user email, upsert user (`email`, `token`) in Postgres, then redirect to `/home` on `FRONTEND_BASE_URL`.

## Database model

`users`

- `id` (UUID string primary key)
- `email` (unique)
- `token` (Google access token)
- `created_at`, `updated_at`
