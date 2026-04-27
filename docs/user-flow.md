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
| Payments | Stripe Checkout (one-time, hosted page) — _integration pending_ |
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
| `id` | VARCHAR(36) PK | UUID |
| `email` | VARCHAR(320) UNIQUE | Google account email |
| `token` | TEXT | Google OAuth access token |
| `created_at` | TIMESTAMPTZ | |
| `updated_at` | TIMESTAMPTZ | |

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

### `payments` _(new — migration 0003)_

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID |
| `user_id` | VARCHAR(36) FK → users NOT NULL | Must be signed in to pay |
| `product_type` | VARCHAR(100) NOT NULL | See product catalogue below |
| `reference_id` | VARCHAR(36) | `analyses.id` for `analysis_access` · `bookings.id` for consultations |
| `stripe_checkout_session_id` | VARCHAR(255) UNIQUE NOT NULL | Set at checkout creation |
| `stripe_payment_intent_id` | VARCHAR(255) UNIQUE | NULL until webhook confirms |
| `stripe_price_id` | VARCHAR(255) | Stripe Price object used — audit trail |
| `stripe_event_id` | VARCHAR(255) | `evt_…` stored for webhook idempotency |
| `amount_cents` | INTEGER NOT NULL | Minor units — never a float |
| `currency` | VARCHAR(10) DEFAULT 'usd' | |
| `status` | VARCHAR(50) DEFAULT 'pending' | `pending \| succeeded \| failed \| expired \| refunded` |
| `metadata` | JSONB DEFAULT '{}' | Product-specific extras |
| `created_at` | TIMESTAMPTZ | |
| `updated_at` | TIMESTAMPTZ | |

```sql
-- Prevents a second successful charge for the same analysis at the DB level
CREATE UNIQUE INDEX uq_payments_analysis_succeeded
  ON payments (reference_id)
  WHERE product_type = 'analysis_access' AND status = 'succeeded';
```

### `bookings` _(new — migration 0004, consultation products only)_

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID |
| `user_id` | VARCHAR(36) FK → users NOT NULL | |
| `payment_id` | VARCHAR(36) FK → payments | NULL until payment confirmed |
| `consultation_type` | VARCHAR(100) NOT NULL | `introductory \| visa \| interview \| cv_sop \| caapid \| license` |
| `duration_minutes` | INTEGER NOT NULL | |
| `status` | VARCHAR(50) DEFAULT 'pending_payment' | `pending_payment \| confirmed \| completed \| cancelled \| no_show` |
| `scheduled_at` | TIMESTAMPTZ | Set when calendar slot is booked |
| `cal_event_id` | VARCHAR(255) | Cal.com / Calendly event ID |
| `notes` | TEXT | Internal prep notes |
| `created_at` | TIMESTAMPTZ | |
| `updated_at` | TIMESTAMPTZ | |

### Product type catalogue

| `product_type` | Stripe price env var | `reference_id` table |
|---|---|---|
| `analysis_access` | `STRIPE_PRICE_ANALYSIS_ACCESS` | `analyses` |
| `consultation_introductory` | `STRIPE_PRICE_CONSULTATION_INTRODUCTORY` | `bookings` |
| `consultation_visa` | `STRIPE_PRICE_CONSULTATION_VISA` | `bookings` |
| `consultation_interview` | `STRIPE_PRICE_CONSULTATION_INTERVIEW` | `bookings` |
| `consultation_cv_sop` | `STRIPE_PRICE_CONSULTATION_CV_SOP` | `bookings` |
| `consultation_caapid` | `STRIPE_PRICE_CONSULTATION_CAAPID` | `bookings` |
| `consultation_license` | `STRIPE_PRICE_CONSULTATION_LICENSE` | `bookings` |

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
appends it as `?analysis_id=` to the backend OAuth login URL. This
round-trips through Google as the OAuth `state` parameter.

```
GET /api/v1/auth/google/login?analysis_id={id}
  FastAPI: state = analysisId
  302 → https://accounts.google.com/o/oauth2/v2/auth?...&state={analysisId}
  (prompt: "consent" — Google always shows the consent screen)

  User approves

GET /api/v1/auth/google/callback?code=…&state={analysisId}
```

**FastAPI callback processing:**
1. `POST https://oauth2.googleapis.com/token` → `access_token`
2. `GET  https://openidconnect.googleapis.com/v1/userinfo` → `email`
3. `upsert_google_user(email, token)` → stable `user_id`
4. `claim_analysis(analysisId, user_id)` → links analysis to user
5. Sets `dentnav_user_id` cookie, redirects to `/landing`

**DB writes:**
```
-- First sign-in:
INSERT users (id=new UUID, email, token)

-- Return visit:
UPDATE users SET token=…, updated_at=now() WHERE email=…

-- Only if analysis_id in state is a valid UUID and row is still anonymous:
UPDATE analyses
  SET user_id = users.id, updated_at = now()
WHERE id = {analysisId} AND user_id IS NULL
```

**Cookie:**
```
Set-Cookie: dentnav_user_id={user.id}; HttpOnly; SameSite=Lax; Max-Age=2592000
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
  POST /api/v1/payments/create-checkout-session
    Cookie: dentnav_user_id={id}
    Body: { product_type: "analysis_access", analysis_id: "…" }

FastAPI:
  1. Reads cookie → 401 if missing
  2. Looks up analysis → 404 if not found
  3. Verifies analysis.user_id == cookie user_id → 403 if not owned
  4. Checks uq_payments_analysis_succeeded index → 409 if already paid
  5. POST https://api.stripe.com/v1/checkout/sessions
  ← { id: "cs_…", url: "https://checkout.stripe.com/…" }

DB write:
  INSERT payments (
    user_id="U1", product_type="analysis_access",
    reference_id=analysisId, stripe_checkout_session_id="cs_…",
    status="pending"
  )

← { checkout_url }
  Browser redirects to Stripe hosted checkout
  User pays
  Stripe redirects to STRIPE_SUCCESS_URL
```

**Stripe webhook `checkout.session.completed`:**
```
POST /api/v1/payments/webhook
  Stripe-Signature: verified against STRIPE_WEBHOOK_SECRET
  Idempotency: skip if stripe_event_id already stored

DB writes:
  UPDATE payments
    SET status="succeeded", stripe_payment_intent_id="pi_…", stripe_event_id="evt_…"
  WHERE stripe_checkout_session_id="cs_…"

  UPDATE analyses SET paid=true WHERE id=payments.reference_id
```

---

### 5.6 Payment — consultation purchase

```
POST /api/v1/payments/create-checkout-session
  Body: { product_type: "consultation_visa" }

FastAPI:
  Resolves duration_minutes (introductory→45, all others→60)

DB writes:
  INSERT bookings (user_id, consultation_type="visa", duration_minutes=60,
                   status="pending_payment")
  INSERT payments (user_id, product_type="consultation_visa",
                   reference_id=bookings.id, status="pending")

Stripe webhook checkout.session.completed:
  UPDATE payments SET status="succeeded", …
  UPDATE bookings SET status="confirmed", payment_id=payments.id

Calendar slot booked (Cal.com / Calendly):
  UPDATE bookings SET scheduled_at=…, cal_event_id=…

Session completed:
  UPDATE bookings SET status="completed"
```

---

## 6. Complete DB state transition table

| User action | Table | Operation | Key columns set |
|---|---|---|---|
| Submit questionnaire | `analyses` | INSERT | `user_id= cookie user or NULL`, `paid=false`, `answers`, `payload` |
| Sign in — first time | `users` | INSERT | `email`, `token` |
| Sign in — return visit | `users` | UPDATE | `token`, `updated_at` |
| OAuth callback with `analysis_id` | `analyses` | UPDATE | `user_id = users.id` |
| Check access status | `analyses` | READ; **or** Case E `DELETE` + READ when a stale unclaimed id is passed | — |
| Create checkout (analysis) | `payments` | INSERT | `status='pending'` |
| Create checkout (consultation) | `bookings` | INSERT | `status='pending_payment'` |
| Create checkout (consultation) | `payments` | INSERT | `status='pending'`, `reference_id=bookings.id` |
| Stripe webhook — analysis | `payments` | UPDATE | `status='succeeded'`, `stripe_payment_intent_id`, `stripe_event_id` |
| Stripe webhook — analysis | `analyses` | UPDATE | `paid=true` |
| Stripe webhook — consultation | `payments` | UPDATE | `status='succeeded'`, `stripe_payment_intent_id`, `stripe_event_id` |
| Stripe webhook — consultation | `bookings` | UPDATE | `status='confirmed'`, `payment_id` |
| Calendar slot booked | `bookings` | UPDATE | `scheduled_at`, `cal_event_id` |
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
| POST | `/api/v1/payments/create-checkout-session` | Yes | INSERT payments (+ bookings for consultations) |
| POST | `/api/v1/payments/webhook` | Stripe-Signature | UPDATE payments + analyses or bookings |

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

# Stripe (payment integration — not yet wired)
STRIPE_SECRET_KEY=sk_test_…
STRIPE_WEBHOOK_SECRET=whsec_…
STRIPE_PRICE_ANALYSIS_ACCESS=price_…
STRIPE_PRICE_CONSULTATION_INTRODUCTORY=price_…
STRIPE_PRICE_CONSULTATION_VISA=price_…
STRIPE_PRICE_CONSULTATION_INTERVIEW=price_…
STRIPE_PRICE_CONSULTATION_CV_SOP=price_…
STRIPE_PRICE_CONSULTATION_CAAPID=price_…
STRIPE_PRICE_CONSULTATION_LICENSE=price_…
STRIPE_SUCCESS_URL=http://localhost:3000/payment/success?session_id={CHECKOUT_SESSION_ID}
STRIPE_CANCEL_URL=http://localhost:3000/landing/packages
```
