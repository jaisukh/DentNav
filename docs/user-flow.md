# DentNav — Request Lifecycle & User Flow

> **Scope:** Covers the full user journey from first visit to full-analysis
> access, including route protection, payment integration, and known edge
> cases around multiple questionnaire submissions. Each step notes which
> database rows are created, updated, or read.

---

## 1. Stack snapshot

| Layer | Technology |
|---|---|
| Frontend | Next.js 16.2.1 (App Router, Turbopack) |
| Route guard | `middleware.ts` (Next.js Edge) + `AuthGuard` client component |
| Backend | FastAPI (Python 3.12, async) |
| Database | PostgreSQL 16 · SQLAlchemy 2 async · Alembic |
| Auth | Google OAuth 2.0 (backend-side redirect, signed JWT in httpOnly cookie, CSRF nonce on `state`) |
| CORS | `expose_headers` includes `X-Removed-Stale-Questionnaire` (read by the Next app) |
| Payments | Razorpay (JS popup, HMAC verification) — _integration pending_ |
| AI | OpenAI (GPT-4o) |
| Storage | AWS S3 (questionnaire JSON) with local-file fallback |

---

## 2. Route protection

The `/landing/*` route group is the authenticated app shell. It is guarded
by two independent layers that run in sequence.

### Layer 1 — `middleware.ts` (Edge, runs before render)

`frontend/middleware.ts` is checked by Next.js before any page in `/landing/**`
is rendered. It reads the `dentnav_user_id` httpOnly cookie.

```
Cookie absent  →  302 redirect to /auth/login?next={pathname}
               (no page rendered, no React code runs)

Cookie present →  NextResponse.next() — request continues to the page
```

This is a presence check only. It cannot verify the JWT signature against the
backend's secret because Edge functions cannot reach the FastAPI server
synchronously. The signature check happens in Layer 2 via
`verify_session_token` on the backend.

> ⚠️ The filename and exported function name are both required by Next.js —
> the file MUST be named `middleware.ts` (or `.js`) and export a function
> named `middleware`. Renaming either silently disables the guard. A
> previous iteration of this file was named `proxy.ts`, which let
> unauthenticated users reach `/landing/*` until the AuthGuard fired.

### Layer 2 — `AuthGuard` (Client component, inside landing layout)

`frontend/components/landing/AuthGuard.tsx` wraps the entire landing layout.
It calls `GET /api/v1/analysis/access-status` on first mount to confirm
the session is still valid with the backend. The request includes an
optional query parameter `local_analysis_id` set from
`localStorage["dentnav:analysis-id"]` when present (see **Case E** in §7).

If the backend removed a **stale second questionnaire** (same user already
had a claimed analysis, but `local_analysis_id` pointed at a different
**unclaimed** row), the response sets the header
`X-Removed-Stale-Questionnaire: 1`. The JSON body is unchanged
(`AnalysisAccessStatusResponse` only). The client detects the header,
runs `applyStaleRemovalSync` so `localStorage["dentnav:analysis-id"]`
matches `latestAnalysisId` from the body, and shows a one-time toast
explaining that only one questionnaire is kept.

| `signedIn` response | AuthGuard renders |
|---|---|
| _in-flight_ | Full-screen "Authenticating…" spinner |
| `true` | Landing layout + page content |
| `false` | Full-screen "Authentication failed" message, then `router.replace("/auth/login?reason=session_expired")` after 2.5 s |

**Layout persistence:** Because `AuthGuard` lives in the layout, it mounts
once when the browser first enters `/landing/*` and does not re-run on
navigation between `/landing`, `/landing/packages`, and `/landing/about`.

### Protected vs. public routes

| Route | middleware.ts | AuthGuard | Accessible without auth |
|---|---|---|---|
| `/` | No | No | Yes |
| `/questionnaire` | No | No | Yes — intentionally anonymous |
| `/analysis` | No | No | Yes — preview from sessionStorage |
| `/auth/login` | No | No | Yes |
| `/about` | No | No | Yes |
| `/landing` | **Yes** | **Yes** | No |
| `/landing/packages` | **Yes** | **Yes** | No |
| `/landing/about` | **Yes** | **Yes** | No |

> **"Get Access"** on `/landing/packages` is therefore unreachable without
> a valid session. Unauthenticated users are redirected to `/auth/login`
> by `middleware.ts` before the page renders.

---

## 3. Database tables

### `users`

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID v4 |
| `email` | VARCHAR(320) UNIQUE NOT NULL | Google account email |
| `first_name` | VARCHAR(120) NOT NULL | Default `''` — populated from Google userinfo |
| `last_name` | VARCHAR(120) NOT NULL | Default `''` — populated from Google userinfo |
| `has_filled` | BOOLEAN NOT NULL | Set `true` when analysis is claimed to this user |
| `created_at` | TIMESTAMPTZ NOT NULL | |
| `updated_at` | TIMESTAMPTZ NOT NULL | |

> The `token` column (Google OAuth access token) existed in migration 0001 and
> was dropped in migration 0003. Tokens are no longer persisted — the session
> is managed via a signed JWT cookie (`dentnav_user_id`) issued at OAuth
> callback time.

### `analyses`

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID |
| `user_id` | VARCHAR(36) FK → users | NULL until claimed via OAuth callback |
| `paid` | BOOLEAN | `false` until payment webhook fires — **the access gate** |
| `country` | VARCHAR(120) | Extracted from LLM payload |
| `degree` | VARCHAR(120) | Extracted from LLM payload |
| `years_of_exp` | VARCHAR(120) | Extracted from LLM payload |
| `performance` | INTEGER | Overall readiness score (0–100) |
| `answers` | JSONB | Raw questionnaire answers |
| `payload` | JSONB | Full LLM response — server-only until paid |
| `created_at` | TIMESTAMPTZ | |
| `updated_at` | TIMESTAMPTZ | |

> **Auth on submit:** If the browser sends a valid `dentnav_user_id` cookie,
> `POST /api/v1/analysis` persists the new row with `user_id` set to that
> user. If the cookie is absent, the row is created with `user_id=NULL` and
> can be claimed later via the OAuth callback `state` param. See §7 for
> edge cases when `localStorage` and multiple rows diverge.

### `services` _(new — migration 0004)_

Single source of truth for every purchasable product. Seeded once; prices and
Calendly event UUIDs updated in-place — no redeploy needed.

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID v4 |
| `slug` | VARCHAR(100) UNIQUE NOT NULL | `analysis_access`, `consultation_visa`, … |
| `name` | VARCHAR(255) NOT NULL | Display name shown in the UI |
| `description` | TEXT NOT NULL DEFAULT `''` | |
| `category` | VARCHAR(50) NOT NULL | `analysis` \| `consultation` |
| `duration_minutes` | INTEGER | NULL for `analysis` category |
| `amount` | INTEGER NOT NULL | Price in the currency's minor unit (e.g. cents for USD) — never a float |
| `currency` | VARCHAR(10) NOT NULL DEFAULT `'usd'` | |
| `calendly_event_type_uuid` | VARCHAR(255) | NULL for `analysis` category |
| `is_active` | BOOLEAN NOT NULL DEFAULT `true` | Soft-disable without deleting |
| `created_at` | TIMESTAMPTZ NOT NULL | |
| `updated_at` | TIMESTAMPTZ NOT NULL | |

### `payments` _(new — migration 0005)_

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID v4 |
| `user_id` | VARCHAR(36) FK → users NOT NULL | Must be signed in to pay |
| `service_id` | VARCHAR(36) FK → services NOT NULL | Which service was purchased |
| `reference_id` | VARCHAR(36) | `analyses.id` for `analysis` · `bookings.id` for consultations |
| `razorpay_order_id` | VARCHAR(255) UNIQUE NOT NULL | `order_ABC` — set at order creation |
| `razorpay_payment_id` | VARCHAR(255) UNIQUE | `pay_XYZ` — set after verification |
| `razorpay_signature` | VARCHAR(512) | HMAC-SHA256 signature — audit trail |
| `amount` | INTEGER NOT NULL | Snapshot of price at time of payment |
| `currency` | VARCHAR(10) NOT NULL DEFAULT `'usd'` | Snapshot from `services.currency` |
| `status` | VARCHAR(50) NOT NULL DEFAULT `'pending'` | `pending \| succeeded \| failed \| expired \| refunded` |
| `metadata` | JSONB NOT NULL DEFAULT `'{}'` | Error codes, refund reason, etc. |
| `created_at` | TIMESTAMPTZ NOT NULL | |
| `updated_at` | TIMESTAMPTZ NOT NULL | |

```sql
CREATE UNIQUE INDEX uq_payments_analysis_succeeded
  ON payments (reference_id)
  WHERE service_id = (SELECT id FROM services WHERE slug = 'analysis_access')
    AND status = 'succeeded';
```

### `bookings` _(new — migration 0006, consultation services only)_

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID v4 |
| `user_id` | VARCHAR(36) FK → users NOT NULL | |
| `service_id` | VARCHAR(36) FK → services NOT NULL | Determines duration + Calendly event type |
| `payment_id` | VARCHAR(36) FK → payments | NULL until payment succeeds |
| `status` | VARCHAR(50) NOT NULL DEFAULT `'pending_payment'` | `pending_payment \| confirmed \| completed \| cancelled \| no_show` |
| `slot_time` | TIMESTAMPTZ | Slot chosen by user (soft-locked in Redis before payment) |
| `slot_expires_at` | TIMESTAMPTZ | `slot_time + 15 min` — hard DB deadline |
| `scheduled_at` | TIMESTAMPTZ | Set by Calendly after event confirmed |
| `calendly_event_id` | VARCHAR(255) | Calendly event UUID |
| `calendly_invitee_url` | TEXT | Calendly invitee link for cancellations |
| `notes` | TEXT | Internal prep notes |
| `created_at` | TIMESTAMPTZ NOT NULL | |
| `updated_at` | TIMESTAMPTZ NOT NULL | |

> `duration_minutes` and `calendly_event_type_uuid` are read from `services`
> at booking time — not stored on `bookings` directly.

### Product catalogue

| `services.slug` | `category` | `duration_minutes` | `reference_id` table |
|---|---|---|---|
| `analysis_access` | `analysis` | — | `analyses` |
| `consultation_introductory` | `consultation` | 45 | `bookings` |
| `consultation_visa` | `consultation` | 60 | `bookings` |
| `consultation_interview` | `consultation` | 60 | `bookings` |
| `consultation_cv_sop` | `consultation` | 60 | `bookings` |
| `consultation_caapid` | `consultation` | 60 | `bookings` |
| `consultation_license` | `consultation` | 60 | `bookings` |

> Prices and Calendly event UUIDs are stored as rows in `services`, not as env vars.

---

## 4. Browser storage

| Store | Key | Written | Cleared | Survives tab close |
|---|---|---|---|---|
| `sessionStorage` | `dentnav:analysis-handoff:{uuid}` | questionnaire submit | `/analysis` page read | No |
| `sessionStorage` | `dentnav:analysis-result` | questionnaire submit | `/analysis` page read | No |
| `localStorage` | `dentnav:analysis-id` | questionnaire submit | Never (manual only) | Yes |
| Cookie (httpOnly) | `dentnav_user_id` | OAuth callback | Sign-out or 30-day expiry | Yes |

`localStorage["dentnav:analysis-id"]` is a **single slot**. Every new
questionnaire submission overwrites the previous value. `getGoogleSignInUrl()`
reads this key to construct the OAuth login URL with `?analysis_id=`, so
only the most recent submission's analysis is ever claimed on sign-in.

After `GET /api/v1/analysis/access-status`, if the server removed a duplicate
unclaimed row (Case E, §7), the client sets this key to `latestAnalysisId` from
the same response so it stays aligned with the analysis the dashboard uses.

---

## 5. Full request lifecycle

### 5.1 Anonymous questionnaire submission

```
1.  GET /                     public home — no API call
2.  GET /questionnaire        Next.js renders QuestionnaireView (public, no proxy check)
3.  GET /api/v1/questionnaire FastAPI reads question JSON from S3 / local file — no DB read
4.  User fills form
5.  POST /api/v1/analysis  { answers: { … } }
      credentials: include  (cookie sent if present)
```

**FastAPI processing:**
1. Validates answers against the questionnaire schema.
2. Calls OpenAI API (~5–15 s) → receives full LLM payload.
3. Extracts `country`, `degree`, `years_of_exp`, `performance`.
4. Persists with `user_id` from the `dentnav_user_id` cookie when present, else `NULL`.
5. Returns the preview slice — `payload` is never included.

**DB write:**
```
INSERT analyses (
  id           = new UUID,
  user_id      = cookie user id or NULL,
  paid         = false,
  country, degree, years_of_exp, performance,
  answers      = { raw answers },
  payload      = { full LLM output }   ← server-only
)
```

**Frontend after response:**
```
handoffId = crypto.randomUUID()
sessionStorage["dentnav:analysis-handoff:{handoffId}"] = payload
sessionStorage["dentnav:analysis-result"]              = payload
localStorage["dentnav:analysis-id"]                   = analysisId   ← overwrites previous
router.push("/analysis?h={handoffId}")
```

**`/analysis` page:**
- Reads `sessionStorage["dentnav:analysis-handoff:{handoffId}"]`
- Renders readiness score, dimensions, strengths, gaps, profile snapshot
- Deletes the handoff key; clears `"dentnav:analysis-result"`
- `localStorage["dentnav:analysis-id"]` remains intact

---

### 5.2 Google sign-in with analysis claim

`getGoogleSignInUrl()` reads `localStorage["dentnav:analysis-id"]` and
appends it as `?analysis_id=` to the backend OAuth login URL.

```
GET /api/v1/auth/google/login?analysis_id={id}

  FastAPI:
    1. Generates CSRF nonce via generate_csrf_nonce()
    2. Sets cookie: oauth_nonce={nonce}  (httpOnly, 5 min, path=/callback)
    3. If analysis_id is a valid UUID:
         Sets cookie: oauth_analysis_id={id}  (httpOnly, 5 min, path=/callback)
         ← analysis_id never goes to Google; it stays server-side in the cookie
    4. 302 → https://accounts.google.com/o/oauth2/v2/auth?...&state={nonce}
       (state = CSRF nonce only, NOT the analysis_id)

  User approves

GET /api/v1/auth/google/callback?code=…&state={nonce}
```

> **Why a cookie instead of `state`:** Passing `analysis_id` through the
> OAuth `state` round-trip (frontend → Google → backend) would expose it in
> browser history and referrer headers. Storing it in an httpOnly path-scoped
> cookie keeps it server-side and burns it immediately after the callback.

**FastAPI callback processing:**
1. Verifies CSRF: `state` query param must match `oauth_nonce` cookie → 400 if mismatch
2. `POST https://oauth2.googleapis.com/token` → `access_token`
3. `GET  https://openidconnect.googleapis.com/v1/userinfo` → `email`, `given_name`, `family_name`
4. Upsert user → stable `user_id`
5. Reads `oauth_analysis_id` cookie:
   - If user **already has a claimed analysis**: `delete_stale_unclaimed_for_double_submit()` → drops the new row → redirect to `/landing?reclaimed_existing=1`
   - If user **has no claimed analysis yet**: `claim_analysis(analysisId, user_id)` → links row to user
6. Burns short-lived cookies (`oauth_nonce`, `oauth_analysis_id`)
7. Sets `dentnav_user_id` cookie, redirects to `/landing`

**DB writes:**
```
-- First sign-in:
INSERT users (id=new UUID, email, first_name, last_name, has_filled=false)

-- Return visit:
UPDATE users SET first_name=…, last_name=…, updated_at=now() WHERE email=…

-- Claim (user has no prior analysis):
UPDATE analyses
  SET user_id = users.id, updated_at = now()
WHERE id = {analysisId} AND user_id IS NULL

UPDATE users SET has_filled = true WHERE id = users.id

-- Double-submit (user already has a claimed analysis):
DELETE FROM analyses WHERE id = {analysisId} AND user_id IS NULL
```

**Cookie set on callback:**
```
Set-Cookie: dentnav_user_id={signed_jwt}; HttpOnly; SameSite=Lax; Max-Age=2592000
(SameSite=None; Secure in production)
```

---

### 5.3 Landing dashboard

```
GET /landing
  Cookie: dentnav_user_id={user.id}

middleware.ts (Edge):
  cookie present → NextResponse.next()   ← <1 ms, no DB, no API

RootLayout: <AuthStatusProvider> issues exactly one fetch on mount:
  GET /api/v1/analysis/access-status?local_analysis_id={from localStorage or omitted}
    FastAPI: reads cookie → verify_session_token(jwt) → optional cleanup
             (Case E, §7) → queries latest analysis for user
    DB: may DELETE one unclaimed analysis row, then
        SELECT … FROM analyses WHERE user_id=… ORDER BY created_at DESC LIMIT 1
  ← { signedIn:true, hasAnsweredQuestionnaire:true, hasPaid:false, latestAnalysisId:"…" }
  ← (optional) X-Removed-Stale-Questionnaire: 1

The result is exposed via `useAuthStatus()` to every consumer:
  • AuthGuard          → gates the layout (signedIn check)
  • LandingPage        → picks QuestionnairePrompt / PaymentPrompt / ViewAnalysis
  • SignInLink         → opens AlreadySignedInModal when signedIn
  • QuestionnaireLink  → opens QuestionnaireDoneModal when hasAnsweredQuestionnaire
  • OneTimeAccessCTA   → conditional buttons on /landing/packages

Net result: one /access-status request per page load, instead of 3–5.
```

---

### 5.4 Sign-out

```
LandingHeader "Sign out" clicked
  POST /api/v1/auth/google/logout
    FastAPI: response.delete_cookie("dentnav_user_id")
    No DB write
  ← { ok: true }
  router.push("/")   router.refresh()
  Cookie deleted — next visit to /landing redirected by middleware.ts
```

---

### 5.5 Payment — analysis access

```
User is on /landing/packages (auth guaranteed by middleware.ts + AuthGuard)
Clicks "Get Access"

Frontend:
  GET /api/v1/analysis/access-status        ← confirms signedIn + latestAnalysisId
  POST /api/v1/payments/create-order
    Cookie: dentnav_user_id={id}
    Body: { service_slug: "analysis_access", analysis_id: "…" }

FastAPI:
  1. Reads cookie → 401 if missing
  2. Looks up analysis → 404 if not found
  3. Verifies analysis.user_id == cookie user_id → 403 if not owned
  4. Checks uq_payments_analysis_succeeded index → 409 if already paid
  5. SELECT amount, currency FROM services WHERE slug='analysis_access'
  6. INSERT payments (user_id, service_id, reference_id=analysisId, status='pending',
                      amount, currency)
  7. POST https://api.razorpay.com/v1/orders
     { amount, currency, receipt: paymentId, close_by: now()+15min }
  8. UPDATE payments SET razorpay_order_id='order_ABC'

← { order_id, amount, currency, key: RAZORPAY_KEY_ID }
  Frontend opens Razorpay JS popup
  User pays → Razorpay returns { razorpay_payment_id, razorpay_order_id, razorpay_signature }
```

**Verification (primary confirmation path):**
```
POST /api/v1/payments/verify
  Body: { payment_id: "pay_XYZ", order_id: "order_ABC", signature: "sig_…" }

FastAPI:
  generated = HMAC_SHA256(RAZORPAY_KEY_SECRET, "order_ABC|pay_XYZ")
  if generated != signature → 400

DB writes:
  UPDATE payments
    SET status='succeeded', razorpay_payment_id='pay_XYZ', razorpay_signature='sig_…'
  WHERE razorpay_order_id='order_ABC'

  UPDATE analyses SET paid=true WHERE id=payments.reference_id
```

---

### 5.6 Payment — consultation booking

> Full flow with slot locking, Redis soft-lock, failure cases, and Calendly
> event creation is documented in `docs/payment-integration.md`.

```
User selects service → calendar shows available slots (Calendly proxy)
User selects slot   → Redis soft-lock broadcast via WebSocket to all clients

User clicks "Pay Now":
  POST /api/v1/payments/create-order
    Body: { booking_id: "B1" }
  FastAPI:
    INSERT bookings (user_id, service_id, status='pending_payment',
                     slot_time, slot_expires_at=now()+15min)
    INSERT payments (user_id, service_id, reference_id=B1, status='pending',
                     amount, currency)
    POST Razorpay /v1/orders with close_by=slot_expires_at

Razorpay popup → user pays → frontend sends signature to backend
  POST /api/v1/payments/verify
    HMAC check + slot expiry check
    UPDATE payments SET status='succeeded', razorpay_payment_id='pay_XYZ'
    UPDATE bookings SET status='confirmed', payment_id=P1
    POST Calendly API → UPDATE bookings SET calendly_event_id, scheduled_at

Session completed:
  UPDATE bookings SET status='completed'
```

---

## 6. Complete DB state transition table

| User action | Table | Operation | Key columns set |
|---|---|---|---|
| Submit questionnaire | `analyses` | INSERT | `user_id= cookie user or NULL`, `paid=false`, `answers`, `payload` |
| Sign in — first time | `users` | INSERT | `email`, `first_name`, `last_name`, `has_filled=false` |
| Sign in — return visit | `users` | UPDATE | `first_name`, `last_name`, `updated_at` |
| OAuth callback with `analysis_id` | `analyses` | UPDATE | `user_id = users.id` |
| Check access status | `analyses` | READ; **or** Case E `DELETE` + READ when a stale unclaimed id is passed | — |
| Create order (analysis) | `payments` | INSERT + UPDATE | `status='pending'`, `razorpay_order_id` |
| Click Pay Now (consultation) | `bookings` | INSERT | `status='pending_payment'`, `slot_time`, `slot_expires_at` |
| Click Pay Now (consultation) | `payments` | INSERT + UPDATE | `status='pending'`, `razorpay_order_id` |
| POST /payments/verify — analysis | `payments` | UPDATE | `status='succeeded'`, `razorpay_payment_id`, `razorpay_signature` |
| POST /payments/verify — analysis | `analyses` | UPDATE | `paid=true` |
| POST /payments/verify — consultation | `payments` | UPDATE | `status='succeeded'`, `razorpay_payment_id`, `razorpay_signature` |
| POST /payments/verify — consultation | `bookings` | UPDATE | `status='confirmed'`, `payment_id` |
| Calendly event created | `bookings` | UPDATE | `scheduled_at`, `calendly_event_id`, `calendly_invitee_url` |
| Session completed | `bookings` | UPDATE | `status='completed'` |
| Read full analysis | — | READ | — |
| Sign out | — | — | cookie deleted |
| Refund — analysis | `payments` | UPDATE | `status='refunded'` |
| Refund — analysis | `analyses` | UPDATE | `paid=false` |
| Refund — consultation | `payments` | UPDATE | `status='refunded'` |
| Refund — consultation | `bookings` | UPDATE | `status='cancelled'` |

---

## 7. Multiple questionnaire submission edge cases

Most scenarios stem from `localStorage` holding only one `analysisId` at a
time, while the database can have multiple `analyses` rows per user. Signed-in
submits can attach the row to the current user; anonymous submits still use
`user_id=NULL` until OAuth claims by id.

### Case A — Anonymous, submits twice, never signs in

```
Submit 1 → A1 (user_id=NULL)   localStorage = "A1"
Submit 2 → A2 (user_id=NULL)   localStorage = "A2"  ← A1 evicted

A1 is an orphan in the DB. No user will ever claim or pay for it.
```

### Case B — Anonymous, submits twice, then signs in

```
Submit 1 → A1   localStorage = "A1"
Submit 2 → A2   localStorage = "A2"

Sign in with analysis_id="A2"
  → claim A2 to U1
  → A1 remains user_id=NULL (orphan)

Dashboard: shows A2 (correct — only claimed row)
```

### Case C — Signs in first, then submits questionnaire (cookie present on POST)

If the same browser session still has the `dentnav_user_id` cookie when
submitting, `POST /api/v1/analysis` sets `user_id` on the new row, so
`/landing` access-status can see a claimed row without a second OAuth round
trip. If the user submits from a context where the cookie is **not** sent
(e.g. another device or session), behavior falls back to an anonymous row
+ claim flow.

### Case D — Existing user signs out, re-submits, signs back in (handled in OAuth callback)

```
A1: user_id="U1" (paid or unpaid)   localStorage was "A1"

Sign out → cookie deleted → user is anonymous.
Re-submits questionnaire (no cookie):
  A2 created (user_id=NULL)    localStorage = "A2"

Sign in again with state="A2":
  upsert_google_user        → same U1 (token refreshed)
  user_has_claimed_analysis → True (A1 exists)
  → DO NOT claim A2 onto U1
  → delete_stale_unclaimed_for_double_submit deletes A2
  → 302 to /landing?reclaimed_existing=1

/landing reads ?reclaimed_existing=1 and shows the toast
  "You're viewing your previous response."
  AuthGuard's subsequent /access-status call returns A1's id; the page
  syncs localStorage["dentnav:analysis-id"] back to A1 transparently.
```

This entirely supersedes the older "most destructive" Case D path (where the
new submission would shadow a paid row in the dashboard query). Now the new
submission is dropped at sign-in time, before any dashboard query runs.

### Case E — Claimed user, second submit unclaimed in `localStorage` (handled on /landing)

**Scenario:** The user already has at least one **claimed** analysis (same
`user_id`). They submit the questionnaire again **without** a session
cookie (e.g. only `localStorage` updates), so a **new** row is created with
`user_id=NULL` and `localStorage["dentnav:analysis-id"]` becomes that new id.

On the next visit to `/landing/*`, the client calls
`GET /api/v1/analysis/access-status?local_analysis_id={that id}`. The backend
(`delete_stale_unclaimed_for_double_submit` in `analysis_store.py`) checks:

1. `local_analysis_id` is a valid UUID.  
2. The signed-in user has at least one row with `user_id` set.  
3. The row for `local_analysis_id` exists and has `user_id IS NULL`.  

If all are true, that unclaimed row is **deleted**, the response includes
`X-Removed-Stale-Questionnaire: 1` (exposed to the browser via CORS), the JSON
body is still `AnalysisAccessStatusResponse` (no extra fields), and
`AuthGuard` shows a toast. The client syncs `localStorage` to
`latestAnalysisId` from the same response.

The toast and discard happen **only** in this path (not on generic loads).

### Implemented vs. open product fixes

| Status | Change |
|---|---|
| Done | `POST /api/v1/analysis` passes `user_id` from the cookie when present. |
| Done | Stale unclaimed second row removed on `/access-status` with `local_analysis_id` when the user already has a claimed analysis; client uses `X-Removed-Stale-Questionnaire` + toast, `localStorage` sync (no extra JSON fields). |
| Done | OAuth callback drops a new unclaimed row when the user already has any claimed analysis, redirects with `?reclaimed_existing=1`; landing page surfaces a "viewing your previous response" toast. Closes Case D. |
| Done | Signed-in users clicking "Sign In" or the questionnaire CTA see an in-place modal instead of being navigated. See §10. |
| Done | "One-time access" CTA on `/landing/packages` is state-aware (Get access · Review your response · Go to questionnaire). |
| Open | Optional: still prefer paid rows in the "latest" dashboard query (`ORDER BY paid DESC, created_at DESC`) as defence-in-depth. |
| Open | Optional: block or warn re-submission when `hasPaid:true` in the questionnaire UI. |

---

## 8. API surface

### Existing endpoints

| Method | Path | Cookie required | DB write |
|---|---|---|---|
| GET | `/api/v1/questionnaire` | No | — |
| POST | `/api/v1/analysis` | No (if present, `user_id` is set) | INSERT analyses |
| GET | `/api/v1/analysis/access-status`  optional query `local_analysis_id` | Optional | —; may DELETE unclaimed row (Case E, §7) |
| GET | `/api/v1/analysis/me/preview` | Yes | — (latest preview slice for the user; NOT gated by `paid`) |
| GET | `/api/v1/analysis/me/answers` | Yes | — (latest raw answers + questionnaire doc) |
| GET | `/api/v1/analysis/{id}/full` | Yes + `paid=true` | — |
| GET | `/api/v1/auth/google/login` | No | — |
| GET | `/api/v1/auth/google/callback` | No | UPSERT users · UPDATE/DELETE analyses · 302 (may include `?reclaimed_existing=1`) |
| POST | `/api/v1/auth/google/logout` | Yes | — |

### New endpoints (payment integration — pending)

| Method | Path | Cookie required | DB write |
|---|---|---|---|
| GET | `/api/v1/services` | No | — |
| GET | `/api/v1/bookings/available-slots` | Yes | — (Calendly proxy) |
| POST | `/api/v1/bookings/reserve` | Yes | INSERT bookings (`status='pending_payment'`) |
| POST | `/api/v1/bookings/{id}/expire` | Yes | UPDATE bookings + payments |
| POST | `/api/v1/payments/create-order` | Yes | INSERT payments · UPDATE payments (`razorpay_order_id`) |
| POST | `/api/v1/payments/verify` | Yes | UPDATE payments + bookings; INSERT Calendly event |
| POST | `/api/v1/payments/fail` | Yes | UPDATE payments + bookings |
| POST | `/api/v1/payments/webhook/razorpay` | Razorpay-Signature | UPDATE payments + bookings (idempotent backup) |

> Full flow and failure cases documented in `docs/payment-integration.md`.

---

## 9. UX rules for already-signed-in / already-filled users

The marketing pages (`/`, `/about`) and the post-submit preview page
(`/analysis`) all carry the same NavBar with **Sign In** and **Get Started**
CTAs. For signed-in users these CTAs would otherwise re-trigger flows that
make no sense (signing in again, re-filling the questionnaire). To keep the
surface predictable, we render those CTAs through two smart wrappers and a
small set of modals.

### Smart wrappers

| Component | File | Behaviour |
|---|---|---|
| `SignInLink` | `frontend/components/auth/SignInLink.tsx` | If `useAuthStatus().signedIn` is `true`, click opens `AlreadySignedInModal` instead of navigating. Otherwise it falls back to `<Link href="/auth/login">`. |
| `QuestionnaireLink` | `frontend/components/questionnaire/QuestionnaireLink.tsx` | If `signedIn && hasAnsweredQuestionnaire`, click opens `QuestionnaireDoneModal` instead of navigating. Otherwise it navigates to `/questionnaire`. |

Both components are imported by every NavBar, hero/CTA/footer card, the
"About Us" page, and the blurred upsell on `/analysis`. There is no longer
any place in the app where a static `<Link href="/auth/login">` or
`<Link href="/questionnaire">` is rendered for a guest-or-signed-in CTA.

### Modals

`frontend/components/ui/ModalShell.tsx` provides the shared chrome
(centered card, ESC + backdrop click, optional `backdropBlur` to blur the
rest of the screen). All three modals close via the top-right `X` and
**stay on the current page** — they are never used as a route.

| Modal | Trigger | Buttons |
|---|---|---|
| `AlreadySignedInModal` | Signed-in user clicks **Sign In** anywhere | "Go to landing page" → `/landing` |
| `QuestionnaireDoneModal` | Signed-in user with `hasAnsweredQuestionnaire=true` clicks **Get Started / Take questionnaire** | "Preview your analysis" → `/analysis?source=server` (NavBar-only flow); "Go to landing page" → `/landing` |
| `AnswersPreviewModal` | "Review your response" on `/landing/packages` | (read-only) GET `/api/v1/analysis/me/answers`, render Q → A list, blurred backdrop. |

### `/analysis` page — server-fetched preview

The preview page used to require a `sessionStorage` handoff written by
`/questionnaire` right before navigation. With the new modal flows the user
can also reach `/analysis` directly from `QuestionnaireDoneModal` without
a handoff. The page now does:

```
useEffect:
  1. If sessionStorage["dentnav:analysis-preview"] is set → hydrate it (existing behaviour).
  2. Else if URL has ?source=server → GET /api/v1/analysis/me/preview, hydrate from response.
  3. Else → render the empty/loading state as before.
After loading, strip ?source=server from the URL with router.replace.
```

The NavBar on `/analysis` is the same shared NavBar, so its **Sign In**
button automatically opens `AlreadySignedInModal` (it uses `SignInLink`).

### `/landing/packages` — One-time access CTA

`frontend/components/landing/OneTimeAccessCTA.tsx` reads `useAuthStatus()`
and renders one of three shapes:

| Conditions | Buttons rendered |
|---|---|
| `!hasAnsweredQuestionnaire` | "Go to questionnaire" (uses `QuestionnaireLink`) |
| `hasAnsweredQuestionnaire && !hasPaid` | "Get access" (primary, links to checkout) · "Review your response" (opens `AnswersPreviewModal`) |
| `hasAnsweredQuestionnaire && hasPaid` | "View analysis" (links to `/analysis?source=server`) · "Review your response" |

While `auth.ready` is `false` the panel renders a skeleton placeholder so
buttons cannot flicker between states.

### Reclaimed-existing toast on `/landing`

When the OAuth callback drops a duplicate submit (Case D, §7), it appends
`?reclaimed_existing=1` to the redirect. `frontend/app/landing/page.tsx`
reads this query param on mount, shows `InfoToast` with the body
"You're viewing your previous response.", and clears the query param via
`router.replace`.

`frontend/components/ui/InfoToast.tsx` is the generalised version of the
old `DuplicateSubmitToast` used by `AuthGuard` for the
`X-Removed-Stale-Questionnaire` flow. Both flows now share the same toast
component (only the title/body/tone differ).

### Direct URL bypass

These modals are gates on **CTA clicks**, not on routing. A signed-in user
who types `/auth/login` or `/questionnaire` directly into the address bar
still sees those pages. That is intentional: the modal pattern is meant to
prevent confusion in the normal click path, not to block power users who
want to re-fill the questionnaire from scratch.

---

## 10. Environment variables

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:15432/dentnav

# Google OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# OpenAI
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o

# AWS S3 (questionnaire storage — leave empty to use local file)
AWS_REGION=us-east-1
AWS_S3_BUCKET=
AWS_S3_QUESTIONNAIRE_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# CORS / Frontend
BACKEND_CORS_ORIGINS=http://localhost:3000
FRONTEND_BASE_URL=http://localhost:3000
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Razorpay (payment integration — pending)
RAZORPAY_KEY_ID=rzp_live_…
RAZORPAY_KEY_SECRET=…
RAZORPAY_WEBHOOK_SECRET=…

# Calendly (consultation booking — pending)
CALENDLY_API_TOKEN=…
CALENDLY_WEBHOOK_SECRET=…

# Frontend (public — safe to expose)
NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_live_…

# Prices, durations, and Calendly event type UUIDs are stored in the
# `services` DB table (seeded in migration 0004) — not in env vars.
```
