# DentNav — Payment Integration & Consultation Booking

> **Scope:** Complete reference for the database schema, booking flow,
> Razorpay integration, Calendly integration, and edge-case handling.
> Covers both the analysis-access payment (no calendar) and the
> multi-doctor consultation booking flow (with calendar + slot locking).

---

## 1. Current Database Schema

### 1.1 `users` (live — migration 0004)

| Column | Type | Notes |
|---|---|---|
| `user_id` | VARCHAR(36) PK | UUID v4 |
| `email` | VARCHAR(320) UNIQUE NOT NULL | Google account email |
| `first_name` | VARCHAR(120) NOT NULL | |
| `last_name` | VARCHAR(120) NOT NULL | |
| `has_filled_questionnaire` | BOOLEAN NOT NULL | `true` after questionnaire submitted |
| `created_at` | TIMESTAMPTZ NOT NULL | |
| `updated_at` | TIMESTAMPTZ NOT NULL | |

### 1.2 `analyses` (live — migration 0004)

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID v4 |
| `user_id` | VARCHAR(36) FK → users SET NULL | NULL until OAuth claim |
| `performance` | INTEGER NOT NULL | Readiness score 0–100 |
| `answers` | JSONB NOT NULL | Raw questionnaire answers |
| `llm_result` | JSONB NOT NULL | Full LLM response — server-only until payment confirmed |
| `created_at` | TIMESTAMPTZ NOT NULL | |
| `updated_at` | TIMESTAMPTZ NOT NULL | |

Index: `ix_analyses_user_id` on `(user_id)`

> `llm_result` is only released via `GET /api/v1/analysis/{id}/full`, which
> checks for a `succeeded` payment row before returning the payload.
> There is no `paid` column on `analyses` — payment status lives in `payments`.

---

## 2. Planned Tables (migrations 0005 – 0011)

### 2.1 `services` — migrations 0005, 0011

Business product catalogue. Independent of any doctor or Calendly account.

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID v4 |
| `service_key` | VARCHAR(100) UNIQUE NOT NULL | Machine-readable lookup key (e.g. `visa_consultation`) |
| `name` | VARCHAR(255) NOT NULL | Display label |
| `description` | TEXT NOT NULL DEFAULT `''` | |
| `duration_minutes` | INTEGER | NULL → analysis (no calendar). NOT NULL → consultation. |
| `base_amount` | INTEGER NOT NULL | Price in minor unit (cents). 0 = TBD. |
| `currency` | VARCHAR(10) NOT NULL DEFAULT `'usd'` | |
| `is_active` | BOOLEAN NOT NULL DEFAULT `true` | Soft-disable without breaking FK history |
| `created_at` | TIMESTAMPTZ NOT NULL | |
| `updated_at` | TIMESTAMPTZ NOT NULL | |

**Design notes:**
- `service_key` is a stable slug used by backend logic and frontend env vars — never a URL segment.
- Category is derived: `duration_minutes IS NULL` → analysis; `IS NOT NULL` → consultation. No separate `category` column.
- Calendly event type is doctor-specific → lives in `doctor_services`.

**Frontend service catalog approach:** Services are **static on the frontend** — no API call to `/services` on page load. `NEXT_PUBLIC_SERVICE_KEY_*` env vars hold the stable keys; when a user selects a service the frontend reads the env var and passes the key to the booking API. The backend resolves the UUID internally.

**Seed data (migration 0005 + 0011):**

| `service_key` | `name` | `duration_minutes` | Notes |
|---|---|---|---|
| `analysis_access` | Analysis Access | NULL | Unlocks `llm_result` for an analysis |
| `intro_consultation` | Introductory Consultation | 45 | |
| `visa_consultation` | Visa Consultation | 60 | |
| `interview_preparation` | Interview Preparation | 60 | |
| `cv_sop_review` | CV / SOP Review | 60 | |
| `caapid_assistance` | CAAPID Assistance | 60 | |
| `license_guidance` | License Guidance | 60 | |

---

### 2.2 `doctors` — migration 0006

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID v4 |
| `name` | VARCHAR(255) NOT NULL | |
| `bio` | TEXT NOT NULL DEFAULT `''` | |
| `photo_url` | TEXT NOT NULL DEFAULT `''` | |
| `specializations` | TEXT[] NOT NULL DEFAULT `'{}'` | e.g. `['visa','residency']` |
| `calendly_user_uri` | VARCHAR(512) | Fetched once via `GET /users/me` with PAT |
| `calendly_pat` | TEXT | Personal Access Token — **encrypted at rest** |
| `is_active` | BOOLEAN NOT NULL DEFAULT `true` | |
| `created_at` | TIMESTAMPTZ NOT NULL | |
| `updated_at` | TIMESTAMPTZ NOT NULL | |

> `calendly_pat` is never returned by any API. Used server-side only to call
> Calendly on behalf of that doctor. Must be AES-256 encrypted at rest.

---

### 2.3 `doctor_services` — migration 0007

Junction table: which doctor offers which service, and via which Calendly event type.

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID v4 |
| `doctor_id` | VARCHAR(36) FK → doctors CASCADE | |
| `service_id` | VARCHAR(36) FK → services RESTRICT | |
| `calendly_event_type_uuid` | VARCHAR(255) NOT NULL | UUID portion of the event type URI |
| `calendly_event_type_uri` | TEXT NOT NULL | Full URI — used directly in API calls |
| `price_override` | INTEGER | NULL → use `services.base_amount` |
| `is_active` | BOOLEAN NOT NULL DEFAULT `true` | |
| `created_at` | TIMESTAMPTZ NOT NULL | |
| `updated_at` | TIMESTAMPTZ NOT NULL | |

Constraints:
```sql
UNIQUE (doctor_id, service_id)
INDEX ix_doctor_services_service_id ON (service_id)
INDEX ix_doctor_services_doctor_id  ON (doctor_id)
```

**Effective price:** `COALESCE(doctor_services.price_override, services.base_amount)`

**Why this table exists:** Two doctors offering the same service (e.g. "Visa Consultation")
have completely separate Calendly accounts and event types. `doctor_services` is the bridge
that maps a business concept (the service) to a provider-specific Calendly concept (the event
type). Availability is fetched per event type — there is no global doctor availability endpoint
in Calendly.

---

### 2.4 `slot_reservations` — migration 0008 (replaces Redis)

Soft lock on a slot for the 5 minutes between slot selection and payment initiation.

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK DEFAULT `gen_random_uuid()` | |
| `doctor_service_id` | VARCHAR(36) FK → doctor_services CASCADE | |
| `slot_time` | TIMESTAMPTZ NOT NULL | |
| `user_id` | VARCHAR(36) FK → users CASCADE | |
| `expires_at` | TIMESTAMPTZ NOT NULL | `now() + 5 minutes` |
| `created_at` | TIMESTAMPTZ NOT NULL DEFAULT `now()` | |

```sql
UNIQUE (doctor_service_id, slot_time)
INDEX ix_slot_reservations_user_id    ON (user_id)
INDEX ix_slot_reservations_expires_at ON (expires_at)
```

**How the lock works — atomic conditional upsert:**

```sql
INSERT INTO slot_reservations (doctor_service_id, slot_time, user_id, expires_at)
VALUES ($ds_id, $slot_time, $user_id, now() + interval '5 minutes')
ON CONFLICT (doctor_service_id, slot_time) DO UPDATE
  SET user_id    = EXCLUDED.user_id,
      expires_at = EXCLUDED.expires_at
  WHERE slot_reservations.expires_at <= now()  -- only overwrite if expired
RETURNING id;
```

- RETURNING has a row → reservation created (or taken over from an expired one). ✓
- RETURNING empty → slot is currently held by another user → 409.
- Two concurrent requests race on the UNIQUE constraint. PostgreSQL serialises them:
  one wins, one gets nothing. No advisory locks, no daemon, no Redis.

Expired rows are invisible (queries filter `expires_at > now()`). No cleanup daemon
needed on the critical path. A periodic `DELETE WHERE expires_at <= now()` handles housekeeping.

---

### 2.5 `bookings` — migration 0009

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID v4 |
| `user_id` | VARCHAR(36) FK → users RESTRICT | |
| `doctor_service_id` | VARCHAR(36) FK → doctor_services RESTRICT | Captures doctor + service in one FK |
| `payment_id` | VARCHAR(36) FK → payments | NULL until payment succeeds |
| `status` | VARCHAR(50) NOT NULL DEFAULT `'pending_payment'` | See transitions below |
| `slot_time` | TIMESTAMPTZ | Chosen slot (UTC) |
| `slot_expires_at` | TIMESTAMPTZ | 15-minute payment hold TTL |
| `scheduled_at` | TIMESTAMPTZ | Set by Calendly after event confirmed |
| `calendly_event_uri` | TEXT | Full event URI — used for cancellations |
| `calendly_invitee_uri` | TEXT | Invitee URI — user's reschedule/cancel link |
| `notes` | TEXT | |
| `created_at` | TIMESTAMPTZ NOT NULL | |
| `updated_at` | TIMESTAMPTZ NOT NULL | |

```sql
INDEX ix_bookings_user_id           ON (user_id)
INDEX ix_bookings_doctor_service_id ON (doctor_service_id)
INDEX ix_bookings_status            ON (status)
```

**Status transitions:**
```
pending_payment ──► confirmed   payment succeeded + Calendly event created
                ──► cancelled   payment failed | slot expired | user cancelled
confirmed       ──► completed   session done (admin marks)
confirmed       ──► cancelled   user or admin cancels
confirmed       ──► no_show     user missed session
```

---

### 2.6 `payments` — migration 0010

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID v4 |
| `user_id` | VARCHAR(36) FK → users NOT NULL | |
| `doctor_service_id` | VARCHAR(36) FK → doctor_services | NULL for analysis access |
| `reference_id` | VARCHAR(36) | `analyses.id` (analysis) or `bookings.id` (consultation) |
| `razorpay_order_id` | VARCHAR(255) UNIQUE NOT NULL | Set at order creation |
| `razorpay_payment_id` | VARCHAR(255) UNIQUE | Set after verification |
| `razorpay_signature` | VARCHAR(512) | HMAC-SHA256 — stored for audit |
| `amount` | INTEGER NOT NULL | Snapshot at order creation — never a float |
| `currency` | VARCHAR(10) NOT NULL DEFAULT `'usd'` | Snapshot from service |
| `status` | VARCHAR(50) NOT NULL DEFAULT `'pending'` | See transitions below |
| `metadata` | JSONB NOT NULL DEFAULT `'{}'` | Error codes, refund reason, etc. |
| `created_at` | TIMESTAMPTZ NOT NULL | |
| `updated_at` | TIMESTAMPTZ NOT NULL | |

```sql
-- Prevents double-charging for the same analysis
CREATE UNIQUE INDEX uq_payments_analysis_succeeded
  ON payments (reference_id)
  WHERE doctor_service_id IS NULL AND status = 'succeeded';
```

**Status transitions:**
```
pending ──► succeeded   HMAC verified + slot confirmed
        ──► failed      Razorpay payment.failed callback
        ──► expired     slot lock TTL elapsed before payment
        ──► refunded    late payment (Case D) or manual refund
```

---

### 2.7 `calendly_webhook_events` — migration 0011 (optional)

Idempotent audit log of raw Calendly webhook payloads.

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK DEFAULT `gen_random_uuid()` | |
| `event_type` | VARCHAR(100) NOT NULL | `invitee.created` · `invitee.canceled` |
| `calendly_uuid` | VARCHAR(255) UNIQUE NOT NULL | Idempotency key |
| `booking_id` | VARCHAR(36) FK → bookings | |
| `payload` | JSONB NOT NULL | |
| `processed_at` | TIMESTAMPTZ | NULL = not yet processed |
| `created_at` | TIMESTAMPTZ NOT NULL DEFAULT `now()` | |

---

### 2.8 ID Relationship Map

```
services (S1: "Visa Consultation", 60 min)
doctors  (D1: Dr. Priya)
  └── doctor_services (DS1: D1 + S1, event_type_uri=..., price_override=NULL)
        └── slot_reservations (SR1: DS1, slot=10:00, user=U1, expires=+5min)
        └── bookings (B1: DS1, user=U1, status=pending_payment, slot_expires_at=+15min)
              └── payments (P1: user=U1, ds=DS1, ref=B1, status=pending)
                    └── razorpay_order_id = order_ABC
                          └── razorpay_payment_id = pay_XYZ

users (U1)
  └── analyses (A1) ← user_id = U1
  └── bookings (B1) ← user_id = U1
  └── payments (P1) ← user_id = U1

-- analysis access payment (no doctor_services)
payments (P2: user=U1, doctor_service_id=NULL, reference_id=A1.id, status=succeeded)
```

---

## 3. Consultation Booking Flow

### Actors

| Actor | Role |
|---|---|
| Frontend | Next.js — renders calendar UI, opens Razorpay SDK |
| Backend | FastAPI — all business logic, DB writes, Calendly proxy |
| PostgreSQL | Source of truth for locks and state |
| Razorpay | Payment gateway (order creation, checkout, webhooks) |
| Calendly | Source of truth for slot availability + event creation |

---

### 3.1 Service & Doctor Selection

```
Frontend renders a static services list from NEXT_PUBLIC_SERVICE_KEY_* env vars.
No API call needed for the catalog — service names, durations, and prices are hardcoded.

User clicks "Visa Consultation"
  → frontend reads process.env.NEXT_PUBLIC_SERVICE_KEY_VISA_CONSULTATION
    = "visa_consultation"

GET /api/v1/services/{service_key}/doctors
← [{ doctor_id, name, bio, photo_url, specializations, effective_amount, currency }, ...]
  -- effective_amount = COALESCE(ds.price_override, s.base_amount)

User selects Dr. Priya → frontend holds { doctor_service_id: "DS1" } in state
```

---

### 3.2 Availability Fetch

```
GET /api/v1/doctors/{doctor_id}/availability?service_id={id}&date_from=...&date_to=...

Backend:
  1. SELECT calendly_event_type_uri, doctor.calendly_pat
     FROM doctor_services JOIN doctors WHERE ds.id = DS1
  2. GET calendly.com/event_type_available_times
       ?event_type={calendly_event_type_uri}&start_time={}&end_time={}
     Authorization: Bearer {doctor.calendly_pat}
  3. SELECT slot_time FROM bookings
       WHERE doctor_service_id = DS1
         AND status NOT IN ('cancelled')
         AND slot_time BETWEEN $start AND $end
     UNION
     SELECT slot_time FROM slot_reservations
       WHERE doctor_service_id = DS1
         AND expires_at > now()
         AND slot_time BETWEEN $start AND $end
         AND user_id != $current_user
  4. Annotate each Calendly slot: available | reserved | booked

← [{ slot_time, status: "available" | "reserved" | "booked" }, ...]
```

---

### 3.3 Slot Reservation (5-minute soft lock)

```
User picks 10:00 AM → frontend greys slot out immediately (optimistic)

POST /api/v1/bookings/reserve
  Body: { doctor_service_id: "DS1", slot_time: "2026-06-01T10:00:00Z" }

Backend:
  1. Auth check → 401
  2. Confirm doctor_services row is_active → 404
  3. Confirm no confirmed booking exists for this slot → 409
  4. Conditional upsert into slot_reservations (atomic):
       INSERT ... ON CONFLICT DO UPDATE WHERE expires_at <= now()
     → RETURNING empty: slot taken by active reservation → 409
     → RETURNING row: reservation created ✓
  5. DELETE any prior slot_reservation by this user on DS1
     (user switching slots before paying)

← { reservation_id: "SR1", slot_time: "...", expires_at: "+5min" }

Frontend: starts 5-minute countdown
  If countdown hits 0 → POST /bookings/reserve/release → slot released
```

---

### 3.4 Order Creation (promote to 15-minute hard lock)

```
User clicks "Proceed to Payment"

POST /api/v1/payments/create-order
  Body: { doctor_service_id: "DS1", slot_time: "2026-06-01T10:00:00Z" }

Backend:
  1. Auth check → 401
  2. Verify slot_reservation exists for this user + DS1 + slot_time, expires_at > now() → 409
  3. Effective price: COALESCE(ds.price_override, s.base_amount)
  4. INSERT bookings (
       status         = 'pending_payment',
       slot_time      = '2026-06-01T10:00:00Z',
       slot_expires_at = now() + 15 min
     )
  5. INSERT payments (status='pending', amount, currency snapshot)
  6. POST razorpay.com/v1/orders {
       amount, currency, receipt=P1.id,
       close_by = unix(slot_expires_at),  ← Razorpay rejects payment after this
       notes: { payment_id, booking_id, user_id }
     }
  7. UPDATE payments SET razorpay_order_id = 'order_ABC'
  8. DELETE slot_reservations WHERE id = SR1   ← hand off; booking is now the lock

← { order_id: "order_ABC", amount, currency, booking_id: "B1",
    expires_at: "...", razorpay_key: "rzp_live_..." }

Frontend:
  Replaces 5-min timer with 15-min timer
  Opens Razorpay checkout modal
```

---

### 3.5 Razorpay Checkout (frontend)

```javascript
const rzp = new Razorpay({
  key:         "rzp_live_...",
  order_id:    "order_ABC",
  amount:      5000,
  currency:    "inr",
  name:        "DentNav",
  description: "Visa Consultation — 60 min with Dr. Priya",
  prefill:     { name: "...", email: "..." },
  handler: function(response) {
    // Payment captured — send to backend for verification
    verifyPayment(response)
  },
  modal: {
    ondismiss: function() {
      // User closed modal — 15-min timer still running, slot still held
    }
  }
})
rzp.open()
```

---

### 3.6 Payment Verification (success path)

```
Razorpay handler fires: { razorpay_payment_id, razorpay_order_id, razorpay_signature }

POST /api/v1/payments/verify
  Body: { payment_id: "pay_XYZ", order_id: "order_ABC", signature: "sig_..." }

Backend:
  Step 1 — HMAC signature check
    generated = HMAC_SHA256(RAZORPAY_KEY_SECRET, "order_ABC|pay_XYZ")
    generated != signature → 400

  Step 2 — Atomic slot confirm (eliminates TOCTOU race)
    UPDATE bookings
      SET status     = 'confirmed',
          payment_id = 'P1',
          updated_at = now()
    WHERE id = 'B1'
      AND status = 'pending_payment'
      AND slot_expires_at > now()
    RETURNING id

    → RETURNING empty: slot expired or already confirmed
      → refund immediately via Razorpay API → 409

  Step 3 — Record payment
    UPDATE payments
      SET status              = 'succeeded',
          razorpay_payment_id = 'pay_XYZ',
          razorpay_signature  = 'sig_...',
          updated_at          = now()
    WHERE razorpay_order_id = 'order_ABC'

  Step 4 — Trigger Calendly event creation (background task)

← { ok: true, booking_id: "B1", slot_time: "...", doctor_name: "..." }
```

---

### 3.7 Calendly Event Creation (background, after 3.6)

```
Backend:
  1. SELECT calendly_event_type_uri, doctor.calendly_pat
     FROM doctor_services JOIN doctors WHERE ds.id = DS1

  2. Re-verify slot still available in Calendly (external booking guard):
     GET calendly.com/event_type_available_times?...
     If slot gone → cancel booking → refund → notify user

  3. POST calendly.com/scheduled_events {
       event_type_uri, start_time,
       invitee: { name, email }
     }
     Authorization: Bearer {doctor.calendly_pat}

  4. UPDATE bookings
       SET scheduled_at        = '2026-06-01T10:00:00Z',
           calendly_event_uri  = 'https://api.calendly.com/scheduled_events/EVT123',
           calendly_invitee_uri = 'https://calendly.com/cancellations/...',
           updated_at          = now()
     WHERE id = 'B1'

Calendly sends confirmation email to user automatically.
```

---

### 3.8 Failure Cases

**Case A — Card declined / Razorpay failure**
```
Razorpay payment.failed callback fires in frontend

POST /api/v1/payments/fail
  Body: { order_id: "order_ABC", error: { ... } }

Backend:
  UPDATE payments SET status='failed', metadata={ error } WHERE razorpay_order_id='order_ABC'
  UPDATE bookings  SET status='cancelled'                  WHERE id='B1'

Frontend → redirect to services with error toast
```

**Case B — Slot expired (frontend countdown)**
```
15-min countdown hits 0

POST /api/v1/bookings/reserve/release  (or /bookings/{id}/expire)

Backend:
  UPDATE bookings  SET status='cancelled' WHERE id='B1' AND status='pending_payment'
  UPDATE payments  SET status='expired'   WHERE reference_id='B1' AND status='pending'

Frontend → redirect to calendar: "Slot expired — please pick a new time"
```

**Case C — HMAC signature mismatch**
```
POST /payments/verify → 400 "signature_mismatch"

Booking and payment remain in pending state.
No money moves (Razorpay captured nothing; signature check is before any DB write).
Cleanup job or next expiry call marks them expired.
```

**Case D — Payment arrives after slot expired (late payment)**
```
Primary defence: Razorpay order has close_by = unix(slot_expires_at)
  → Razorpay rejects at gateway: no money moves, nothing to refund.

Secondary defence (belt-and-suspenders): if Razorpay somehow processes past close_by:
  POST /payments/verify Step 2:
    bookings.status = 'cancelled' OR slot_expires_at < now()
    → RETURNING empty → LATE PAYMENT DETECTED

  Immediate refund:
    POST razorpay.com/payments/pay_XYZ/refund { amount }

  UPDATE payments SET status='refunded', metadata={ refund_reason:'slot_expired' }

← 409 { error: "slot_expired", message: "Slot expired. Full refund initiated." }
```

**Case E — External Calendly booking takes the slot**
```
Detected during Calendly event creation (Step 3.7 re-verification):
  Slot no longer in available_times response

Backend:
  UPDATE bookings SET status='cancelled'
  POST razorpay.com/payments/pay_XYZ/refund
  UPDATE payments SET status='refunded', metadata={ refund_reason:'slot_taken_externally' }
  Notify user via email/webhook

Also detected proactively via Calendly invitee.created webhook:
  Cross-check against any pending_payment bookings for same slot
  If match → cancel + refund before user pays
```

---

### 3.9 Razorpay Webhook (backup confirmation)

```
POST /api/v1/payments/webhook/razorpay
  Verify: X-Razorpay-Signature against RAZORPAY_WEBHOOK_SECRET

Events:
  payment.captured:
    1. Look up payment by razorpay_order_id
    2. Skip if status already 'succeeded' or 'refunded' (idempotent)
    3. Run Step 2 slot check (Case D)
    4. Run same DB writes as §3.6
    5. Create Calendly event if calendly_event_uri IS NULL

  payment.failed:
    UPDATE payments SET status='failed'
    UPDATE bookings  SET status='cancelled' if still pending_payment

  refund.processed:
    UPDATE payments SET status='refunded'
```

> **Primary path:** frontend `handler` → `POST /verify`.
> **Backup path:** Razorpay webhook → fires if the tab was closed after payment
> but before verify completed.

---

## 4. Analysis Access Payment Flow

Simpler variant — no calendar, no slot locking.

```
1. User on /landing/analysis (has completed questionnaire, not yet unlocked)
   GET /api/v1/analysis/access-status → { hasAnsweredQuestionnaire: true, hasPaid: false }

2. User clicks "Unlock Full Analysis"
   POST /api/v1/payments/create-order
     Body: { reference_id: "A1" }   -- analyses.id

   Backend:
     SELECT id FROM services WHERE service_key = 'analysis_access'
       -- the "Analysis Access" service row
     INSERT payments (
       user_id          = U1,
       doctor_service_id = NULL,
       reference_id     = 'A1',
       amount           = services.base_amount,
       currency         = services.currency,
       status           = 'pending'
     )
     POST razorpay.com/v1/orders { amount, currency, receipt=P1.id }
     UPDATE payments SET razorpay_order_id = 'order_ABC'
   ← { order_id, amount, currency, key }

3. Frontend opens Razorpay modal. User pays.

4. POST /api/v1/payments/verify { payment_id, order_id, signature }
   Backend:
     HMAC check → 400 if mismatch
     UPDATE payments
       SET status='succeeded', razorpay_payment_id, razorpay_signature
     WHERE razorpay_order_id='order_ABC'
       AND status='pending'
     RETURNING id

   -- No booking/slot logic. No Calendly.

   ← { ok: true, analysis_id: "A1" }

5. GET /api/v1/analysis/{A1}/full
   Backend:
     SELECT EXISTS(
       SELECT 1 FROM payments
       WHERE reference_id = 'A1'
         AND status = 'succeeded'
         AND doctor_service_id IS NULL
     ) → 402 if false
     Return analysis.llm_result
```

---

## 5. Concurrency & Idempotency

| Endpoint | Strategy |
|---|---|
| `POST /bookings/reserve` | Conditional upsert on UNIQUE(doctor_service_id, slot_time) |
| `POST /payments/create-order` | Check existing pending payment for same user+DS+slot first |
| `POST /payments/verify` | `WHERE status='pending_payment' AND slot_expires_at > now()` — second call is no-op |
| `POST /payments/webhook/razorpay` | `WHERE status != 'succeeded'` guard before any write |
| Calendly webhook | `INSERT ... ON CONFLICT (calendly_uuid) DO NOTHING` |

---

## 6. Calendly Integration Notes

- Calendly availability is always fetched **per event type**, never per doctor globally.
- `doctor_services.calendly_event_type_uri` is the bridge from business concept to Calendly concept.
- Each doctor authenticates via their own PAT (`doctors.calendly_pat`) — no shared token.
- `calendly_user_uri` is fetched once at doctor onboarding via `GET /users/me` and cached.
- Calendly remains the **source of truth** for availability — we never mirror it.
- External bookings made directly in Calendly are detected via the `invitee.created` webhook and via re-verification before event creation.

---

## 7. Calendly Sync Strategy

| Trigger | When | Action |
|---|---|---|
| Doctor onboarding | Admin adds doctor | `GET /event_types?user={uri}` → seed `doctor_services` rows |
| Admin on-demand | "Sync" button | Same — idempotent upsert |
| Periodic | Weekly background job | Detect deleted/changed event types → soft-disable stale rows |
| Calendly webhook | `event_type.*` events | Update or soft-delete affected `doctor_services` rows |

---

## 8. Migration Plan

| Migration | Contents |
|---|---|
| 0005 | Create `services`, seed rows |
| 0006 | Create `doctors` |
| 0007 | Create `doctor_services` |
| 0008 | Create `slot_reservations` |
| 0009 | Create `bookings` |
| 0010 | Create `payments` + deferred `bookings.payment_id` FK |
| 0011 | Add `service_key` to `services`, seed values |
| 0012 | Create `calendly_webhook_events` (optional) |

---

## 9. Environment Variables

```bash
# Razorpay
RAZORPAY_KEY_ID=rzp_live_...
RAZORPAY_KEY_SECRET=...
RAZORPAY_WEBHOOK_SECRET=...

# Calendly
CALENDLY_WEBHOOK_SIGNING_KEY=...   # verifying Calendly webhook payloads
# No global CALENDLY_API_TOKEN — each doctor's PAT lives in doctors.calendly_pat

# Frontend (public)
NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_live_...

# Service keys — must match service_key values in the services table
# Frontend uses these to pass a stable key to the booking API without hardcoding UUIDs
NEXT_PUBLIC_SERVICE_KEY_ANALYSIS_ACCESS=analysis_access
NEXT_PUBLIC_SERVICE_KEY_INTRO_CONSULTATION=intro_consultation
NEXT_PUBLIC_SERVICE_KEY_VISA_CONSULTATION=visa_consultation
NEXT_PUBLIC_SERVICE_KEY_INTERVIEW_PREPARATION=interview_preparation
NEXT_PUBLIC_SERVICE_KEY_CV_SOP_REVIEW=cv_sop_review
NEXT_PUBLIC_SERVICE_KEY_CAAPID_ASSISTANCE=caapid_assistance
NEXT_PUBLIC_SERVICE_KEY_LICENSE_GUIDANCE=license_guidance
```
